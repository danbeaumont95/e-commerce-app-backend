from fastapi import APIRouter, Body, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..basket.model import BasketModel, ItemToAdd
from ..db import db
from .item import decodeJWT

router = APIRouter(
    prefix="/basket",
    tags=['basket']
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


@router.post('/')
async def create_basket(basket: BasketModel = Body(...)):
    basket = jsonable_encoder(basket)
    if basket['items'] == None:
        basket['items'] = []

    new_basket = await db['baskets'].insert_one(basket)
    created_basket = await db['users'].find_one({"_id": new_basket.inserted_id})

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_basket)


@router.post('/addToBasket')
async def add_item_to_basket(request: Request, item: ItemToAdd = Body(...)):

    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:

        user_id = isAllowed['user_id']
        item = jsonable_encoder(item)
        await db['baskets'].update_one({"userId": user_id}, {"$push": {
            "items": item
        }})

        return {
            "Message": "Item added to basket!"
        }
    else:
        return {
            "Message": "Token expired, please log in again"
        }
