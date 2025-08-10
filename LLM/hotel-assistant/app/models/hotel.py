from pydantic import BaseModel

class Location(BaseModel):
    lon: float
    lat: float

class Hotel(BaseModel):
    id: str
    title: str
    description: str
    amenities: dict[str, list[str]]
    location: Location
    highlights: list[str]
    local_tips: list[str]
    url: str
