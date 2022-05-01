from fastapi import APIRouter
from ..user.model import UserModel, UserReturnModel, TestUserLoginSchema, SessionModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Body, HTTPException, status, APIRouter
from collections import namedtuple
import time
from typing import Dict
import jwt
from email_validator import validate_email, EmailNotValidError

from ..db import db, jwt_algorithm, jwt_secret
from .basket import create_basket

router = APIRouter(
    prefix="/user",
    tags=['user']
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, jwt_secret, algorithms=[jwt_algorithm])
        return decoded_token if decoded_token['expires'] >= time.time() else None
    except:
        return {}


def token_response(access_token: str, refresh_token: str):
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def signJWT(user_id: str) -> Dict[str, str]:
    access_payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    refresh_payload = {
        "user_id": user_id,
        "expires": time.time() + 30000000
    }
    access_token = jwt.encode(
        access_payload, jwt_secret, algorithm=jwt_algorithm)
    refresh_token = jwt.encode(
        refresh_payload, jwt_secret, algorithm=jwt_algorithm)
    return token_response(access_token, refresh_token)


async def check_if_user_taken(input: str, value: str):
    user_exists = await db['users'].find_one({f"{value}": input})
    return user_exists


@router.post('/', tags=['user'])
async def create_user(user: UserModel = Body(...)):
    user = jsonable_encoder(user)
    if len(user['firstName']) < 1 or len(user['lastName']) < 1 or len(user['email']) < 1 or len(user['password']) < 1 or len(user['username']) < 1 or len(str(user['mobileNumber'])) < 1:
        return {"error": "Missing required field"}
    try:
        validate_email(user['email']).email
        email_taken = await check_if_user_taken(user['email'], 'email')
        username_taken = await check_if_user_taken(user['username'], 'username')
        mobileNumber_taken = await check_if_user_taken(user['mobileNumber'], 'mobileNumber')

        if email_taken != None:
            return {"error": "Email Already exists"}
        if username_taken != None:
            return {"error": "Username Already exists"}
        if mobileNumber_taken != None:
            return {"error": "Mobile Number Already exists"}

        new_user = await db['users'].insert_one(user)
        created_user = await db['users'].find_one({"_id": new_user.inserted_id})

        await create_basket({"userId": created_user['_id'], "items": []})

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)
    except EmailNotValidError as e:
        return {"error": str(e)}


@router.get('/{id}', tags=['user'], response_description="Gets a user by id", response_model=UserReturnModel)
async def get_user(id: str):
    if (user := await db['users'].find_one({"_id": id})) is not None:
        return user
    raise HTTPException(status_code=404, detail=f"User {id} not found")


# @router.post('/user/createAccessToken')
# async def sign_up(user: TestUserSchema = Body(...)):
#     user = jsonable_encoder(user)
#     await db['users'].insert_one(user)
#     return signJWT(user["email"])

@router.post('/login')
async def login(user: TestUserLoginSchema = Body(...)):
    async def check_user(data=Body(...)):

        all_users = await db['users'].find().to_list(1000)
        for user in all_users:
            del user['_id']
            object_name = namedtuple("ObjectName", user.keys())(*user.values())
            if object_name.email == data.email and object_name.password == data.password:
                return True
        return False

    async def save_token_in_db(token: SessionModel = Body(...), id: str = Body(...)):
        token = jsonable_encoder(token)
        userId = jsonable_encoder(id)
        insert_obj = {"token": token, "userId": userId}
        new_token = await db['user-sessions'].insert_one(jsonable_encoder(insert_obj))
        created_token = await db['user-sessions'].find_one({"_id": new_token.inserted_id})
        return created_token

    async def get_user(email):
        if (user := await db['users'].find_one({"email": email})) is not None:
            return user
        raise HTTPException(status_code=404, detail=f"User {id} not found")

    res = await check_user(user)

    if res:
        user = jsonable_encoder(user)
        user_details = await get_user(user['email'])
        user_id = user_details['_id']
        token = signJWT(user_id)

        await save_token_in_db(token, str(user_id))
        return token
    return {
        "error": "Wrong login details"
    }
