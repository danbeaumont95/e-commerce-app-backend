from fastapi import APIRouter, Body, status, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from ..db import db
from .item import decodeJWT
from ..address.model import AddressModel, AddAddressModel
from bson.objectid import ObjectId
import uuid

router = APIRouter(
    prefix="/address",
    tags=['address']
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


@router.post('/')
async def add_address(request: Request, address: AddAddressModel = Body(...)):
    bearer_token = request.headers.get('authorization')
    formatted_address = jsonable_encoder(address)

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:
        user_id = isAllowed['user_id']

        found_address = await db['addresses'].find_one({"userId": user_id})

        if found_address is None:
            return {"error": "Unable to add address"}

        new_address = {"id": str(uuid.uuid4()), "firstLine": formatted_address['firstLine'], "secondLine": formatted_address['secondLine'],
                       "TownCity": formatted_address['TownCity'], "Postcode": formatted_address['Postcode'], "Country": formatted_address['Country']}

        await db['addresses'].update_one({"userId": user_id}, {"$push": {
            "addresses": new_address
        }})
        return {
            "Message": "Address added!"
        }
    else:
        return {"error": "Token expired! Please log in again!"}
