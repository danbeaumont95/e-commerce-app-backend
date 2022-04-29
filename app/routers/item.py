from fastapi import APIRouter
from ..item.model import ItemModel, UpdateItemModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Body, HTTPException, status, APIRouter, Request
from typing import List
import time
import jwt

from ..db import db, jwt_algorithm, jwt_secret

router = APIRouter(
    prefix="/item",
    tags=['item']
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


@router.get(
    "/", response_description="List all items", response_model=List[ItemModel]
)
async def list_items():
    items = await db["items"].find().to_list(1000)
    return items


@router.put("/{id}", response_description="Updates an item", response_model=ItemModel)
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


@router.get("/{id}", response_description="Gets an item by id", response_model=ItemModel)
async def get_item(id: str):
    if (item := await db['items'].find_one({"_id": id})) is not None:
        return item
    raise HTTPException(status_code=404, detail=f"Item {id} not found")


@router.delete("/{id}", response_description="Deletes an item")
async def delete_item(id: str):
    delete_result = await db['items'].delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Item {id} not found")


@router.post('/', response_description="Add new item")
async def create_new_item(request: Request, item: ItemModel = Body(...)):
    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]

    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:

        item = jsonable_encoder(item)
        created_item = {"description": item['description'],
                        "seller": isAllowed['user_id'], "name": item['name'], "price": item['price']}

        new_item = await db['items'].insert_one(created_item)

        await db["items"].find_one({"_id": new_item.inserted_id})

        return {
            "Message": "Item inserted in DB"
        }
    return {
        "Message": "Token expired, please log in again"
    }
