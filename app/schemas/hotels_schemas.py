from pydantic import BaseModel, ConfigDict


class SHotel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    services: list[str]
    rooms_quantity: int
    image_id: int


class SHotelInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    services: list
    rooms_quantity: int
    image_id: int
    rooms_left: int
