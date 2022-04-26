
import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio
from dotenv import load_dotenv, dotenv_values

config = dotenv_values(".env")
db_name = config['db_name']
db_username = config['db_username']
db_password = config['db_password']

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


@app.post("/item", response_description="Add new item", response_model=ItemModel)
async def create_item(item: ItemModel = Body(...)):
    item = jsonable_encoder(item)
    new_item = await db["items"].insert_one(item)
    created_item = await db["items"].find_one({"_id": new_item.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_item)


@app.get(
    "/", response_description="List all items", response_model=List[ItemModel]
)
async def list_items():
    items = await db["items"].find().to_list(1000)
    return items
