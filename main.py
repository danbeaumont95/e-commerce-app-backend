
import os
from fastapi import FastAPI, Body, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio
from dotenv import load_dotenv, dotenv_values
import time
import jwt
from typing import Dict
from collections import namedtuple

config = dotenv_values(".env")
db_name = config['db_name']
db_username = config['db_username']
db_password = config['db_password']

JWT_SECRET = config["secret"]
JWT_ALGORITHM = config["algorithm"]

# uvicorn main:app --reload
load_dotenv()

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{db_username}:{db_password}@e-commerce-app.z4k96.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = client['e-commerce-app']


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    firstName: str = Field(...)
    lastName: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)
    mobileNumber: int = Field(...)
    username: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "test@email.com",
                "password": "password",
                "username": "janedoe",
                "mobileNumber": 447515538351,
            }
        }


class SessionModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    accessToken: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "accessToken": "accesstoken",
            }
        }


class UserReturnModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    firstName: str = Field(...)
    lastName: str = Field(...)
    email: str = Field(...)
    mobileNumber: int = Field(...)
    username: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "test@email.com",
                "username": "janedoe",
                "mobileNumber": 447515538351,
            }
        }


class ItemModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    seller: str = Field(...)
    description: str = Field(...)
    name: str = Field(...)
    price: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "seller": "Jane Doe",
                "description": "test description",
                "name": "Dan",
                "price": "3.0",
            }
        }


class UpdateItemModel(BaseModel):
    description: Optional[str]
    name: Optional[str]
    price: Optional[int]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "description": "test description",
                "name": "Dan",
                "price": "3.0",
            }
        }


@app.post("/item", response_description="Add new item", response_model=ItemModel)
async def create_item(item: ItemModel = Body(...)):
    item = jsonable_encoder(item)
    new_item = await db["items"].insert_one(item)
    created_item = await db["items"].find_one({"_id": new_item.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item)


@app.get(
    "/item", response_description="List all items", response_model=List[ItemModel]
)
async def list_items():
    items = await db["items"].find().to_list(1000)
    return items


@app.put("/item/{id}", response_description="Updates an item", response_model=ItemModel)
async def update_item(id: str, item: UpdateItemModel = Body(...)):
    item = {k: v for k, v in item.dict().items() if v is not None}
    if len(item) >= 1:
        update_result = await db['items'].update_one({"_id": id}, {"$set": item})
        if update_result.modified_count == 1:
            if (
                updated_item := await db['items'].find_one({"_id": id})
            ) is not None:
                return updated_item
    if (existing_item := await db['items'].find_one({"_id": id})) is not None:
        return existing_item
    raise HTTPException(status_code=404, detail=f"Item {id} not found")


@app.get("/item/{id}", response_description="Gets an item by id", response_model=ItemModel)
async def get_item(id: str):
    if (item := await db['items'].find_one({"_id": id})) is not None:
        return item
    raise HTTPException(status_code=404, detail=f"Item {id} not found")


@app.delete("/item/{id}", response_description="Deletes an item")
async def delete_item(id: str):
    delete_result = await db['items'].delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Item {id} not found")


@app.post('/user')
async def create_user(user: UserModel = Body(...)):
    user = jsonable_encoder(user)
    new_user = await db['users'].insert_one(user)
    created_user = await db['users'].find_one({"_id": new_user.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


@app.get('/user/{id}', response_description="Gets a user by id", response_model=UserReturnModel)
async def get_user(id: str):
    if (user := await db['users'].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=404, detail=f"User {id} not found")


def token_response(token: str):
    return {
        "access_token": token
    }


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token['expires'] >= time.time() else None
    except:
        return {}


class TestUserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "email": "test@hotmail.com",
                "password": "password"
            }
        }


class TestUserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }


@app.post('/user/createAccessToken')
async def sign_up(user: TestUserSchema = Body(...)):
    user = jsonable_encoder(user)
    await db['users'].insert_one(user)
    return signJWT(user["email"])


async def check_user(data: TestUserLoginSchema):
    all_users = await db['users'].find().to_list(1000)
    for user in all_users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


@app.post('/user/login')
async def login(user: TestUserLoginSchema = Body(...)):
    async def check_user(data=Body(...)):

        all_users = await db['users'].find().to_list(1000)
        for user in all_users:
            del user['_id']
            object_name = namedtuple("ObjectName", user.keys())(*user.values())
            if object_name.email == data.email and object_name.password == data.password:
                return True
        return False

    async def save_token_in_db(token: SessionModel = Body(...)):
        token = jsonable_encoder(token)
        new_token = await db['user-sessions'].insert_one(token)
        created_token = await db['user-sessions'].find_one({"_id": new_token.inserted_id})
        return created_token

    res = await check_user(user)

    if res:
        user = jsonable_encoder(user)
        token = signJWT(user["email"])
        await save_token_in_db(token)
        return token
    return {
        "error": "Wrong login details"
    }
