from fastapi import APIRouter, Body, status, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..db import db
from .item import decodeJWT
from ..address.model import AddressModel
from bson.objectid import ObjectId

router = APIRouter(
    prefix="/address",
    tags=['address']
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


@router.post('/')
async def add_address(request: Request, address=Body(...)):
    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:
        user_id = isAllowed['user_id']

        found_address = await db['addresses'].find_one({"userId": user_id})

        if found_address is None:
            return {"error": "Unable to add address"}
        await db['addresses'].update_one({"userId": user_id}, {"$push": {
            "addresses": address
        }})
        return {
            "Message": "Address added!"
        }
