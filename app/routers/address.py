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


@router.put('/{id}')
async def update_address(request: Request, id: str, body=Body(...)):
    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:
        user_id = isAllowed['user_id']

        users_address = await db['addresses'].find_one({"userId": user_id})

        if users_address is None:
            return {"error": "No addresses found"}

        if "firstLine" in body:
            await db['addresses'].find_one_and_update({"userId": user_id, "addresses.id": id}, {"$set": {
                "addresses.$.firstLine": body['firstLine']
            }})
        if "secondLine" in body:
            await db['addresses'].find_one_and_update({"userId": user_id, "addresses.id": id}, {"$set": {
                "addresses.$.secondLine": body['secondLine']
            }})
        if "TownCity" in body:
            await db['addresses'].find_one_and_update({"userId": user_id, "addresses.id": id}, {"$set": {
                "addresses.$.TownCity": body['TownCity']
            }})
        if "Postcode" in body:
            await db['addresses'].find_one_and_update({"userId": user_id, "addresses.id": id}, {"$set": {
                "addresses.$.Postcode": body['Postcode']
            }})
        if "Country" in body:
            await db['addresses'].find_one_and_update({"userId": user_id, "addresses.id": id}, {"$set": {
                "addresses.$.Country": body['Country']
            }})
        return {
            "Message": "Address updated"
        }
    else:
        return {"error": "Token expired! Please log in again!"}


@router.get('/', response_model=AddressModel)
async def get_all_addresses(request: Request):
    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]
    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:
        user_id = isAllowed['user_id']
        if (address := await db['addresses'].find_one({"userId": user_id})) is not None:
            return address
        raise HTTPException(
            status_code=404, detail=f"No addresses found")
    else:
        return {"error": "Token expired! Please log in again!"}
