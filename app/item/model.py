from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional


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
    image: str = Field(...)

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
                "image": "https://python-e-commerce-app.s3.eu-west-2.amazonaws.com/1.jpg"
            }
        }


class UpdateItemModel(BaseModel):
    description: Optional[str]
    name: Optional[str]
    price: Optional[int]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "description": "test description",
                "name": "Dan",
                "price": "3.0",
            }
        }
