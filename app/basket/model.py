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


class BasketModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: str = Field(...)
    items: Optional[tuple]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id": "abc123",
                "userId": "dansId123",
                "items": [
                    {
                      "name": "Playstation",
                      "seller": "dan",
                      "price": 123
                    }
                ]
            }
        }


class ItemToAdd(BaseModel):
    name: str = Field(...)
    seller: str = Field(...)
    price: int = Field(...)
    itemId: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id": "abc123",
                "userId": "dansId123",
                "items": [
                    {
                      "name": "Playstation",
                      "seller": "dan",
                      "price": 123,
                      "itemId": "321"
                    }
                ]
            }
        }
