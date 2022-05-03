import boto3
from fastapi import APIRouter
from pydantic import Field
from ..item.model import ItemModel, UpdateItemModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Body, HTTPException, status, APIRouter, Request, Form, File, UploadFile
from typing import List
import time
import jwt
import os
import datetime
from botocore.exceptions import ClientError


from ..db import db, jwt_algorithm, jwt_secret, aws_access_key_id, aws_secret_access_key

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


async def upload_fileobj(file_name, bucket, key):

    """Upload a file to an S3 bucket
    :param key:
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if (key is None) or (bucket is None):
        print("key and bucket cannot be None")
        return False

    # Upload the file
    s3_client = boto3.client('s3')

    try:

        response = s3_client.upload_fileobj(
            file_name, bucket, key, ExtraArgs={'ACL': 'public-read'})

    except ClientError as e:
        print("INFO: Failed to upload image")
        print(e)
        return False

    print(
        "File object uploaded to https://s3.amazonaws.com/{}{}".format(bucket, key))
    return True


@router.post('/', response_description="Add new item")
async def create_new_item(request: Request, fileobject: UploadFile = File(...), description: str = Body(...), name: str = Body(...), price: str = Body(...)):

    bearer_token = request.headers.get('authorization')

    access_token = bearer_token[7:]

    isAllowed = decodeJWT(access_token)

    if isAllowed is not None:

        filename = fileobject.filename

        current_time = datetime.datetime.now()
        split_file_name = os.path.splitext(filename)

        file_name_unique = str(current_time.timestamp()).replace('.', '')

        file_extension = split_file_name[1]  # file extention

        data = fileobject.file._file  # Converting tempfile.SpooledTemporaryFile to io.BytesIO

        uploads3 = await upload_fileobj(
            data,  'python-e-commerce-app', filename)

        if uploads3:
            created_item = {"description": description,
                            "seller": isAllowed['user_id'], "name": name, "price": price, "image": f"https://python-e-commerce-app.s3.eu-west-2.amazonaws.com/{filename}"}

            new_item = await db['items'].insert_one(created_item)

            return {"status": True, "message": "Item inserted in DB"}
        else:
            raise HTTPException(
                status_code=400, detail="Failed to upload in S3")
    else:
        return {
            "Message": "Token expired, please log in again"
        }
