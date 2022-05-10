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


class AddressModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: str = Field(...)
    addresses: Optional[tuple]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id": "abc123",
                "userId": "dansId123",
                "addresses": [
                    {
                      "firstLine": "1 dan road",
                      "lastLine": "1 second line",
                      "townCity": "Huddersfield",
                      "postcode": "HD1 111",
                      "country": "England"
                    }
                ]
            }
        }


class AddAddressModel(BaseModel):
    firstLine: str = Field(...)
    secondLine: str = Field(...)
    TownCity: str = Field(...)
    Postcode: str = Field(...)
    Country: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id": "abc123",
                "userId": "dansId123",
                "addresses": [
                    {
                      "firstLine": "1 dan road",
                      "lastLine": "1 second line",
                      "townCity": "Huddersfield",
                      "postcode": "HD1 111",
                      "country": "England"
                    }
                ]
            }
        }
