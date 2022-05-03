from fastapi import APIRouter, Body, status, Request, HTTPException
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


@router.get('/', tags=['basket'], response_description='Returns logged in users basket', response_model=BasketModel)
async def get_my_basket(request: Request):
    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:
        user_id = isAllowed['user_id']
        if (basket := await db['baskets'].find_one({"userId": user_id})) is not None:
            return basket
        raise HTTPException(
            status_code=404, detail=f"Your basket was not found")
    else:

        return {
            "error": "Token expired, please log in again"
        }


@router.delete('/{id}', tags=['basket'], response_description='delets an item from basket')
async def delete_item_from_basket(request: Request, id: str):
    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)
    if isAllowed is not None:
        user_id = isAllowed['user_id']
        user_basket = await db['baskets'].find_one({"userId": user_id})

        try:
            await db['baskets'].update_one({"_id": user_basket['_id']}, {"$pull": {
                "items": {"itemId": id}
            }})

            updated_user_basket = await db['baskets'].find_one({"userId": user_id})

            if len(updated_user_basket['items']) < len(user_basket['items']):
                return {"message": "Item deleted"}
            else:
                return {"error": "Unable to delete item"}

        except:
            return {"error": "Unable to delete item"}
    else:
        return {
            "error": "Token expired, please log in again"
        }


@router.get('/amount', tags=['basket'], response_description='Gets amount of items in basket')
async def get_amount_of_items_in_basket(request: Request):

    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]

    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:
        user_id = isAllowed['user_id']
        user_basket = await db['baskets'].find_one({"userId": user_id})
        items = user_basket['items']

        return {"amount": len(items)}
    else:

        return {"error": "Token expired, please log in again"}
