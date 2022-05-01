from fastapi import APIRouter, Body, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..basket.model import BasketModel
from ..db import db

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
