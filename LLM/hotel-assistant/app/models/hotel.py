from pydantic import BaseModel
from typing import List, Dict

class Location(BaseModel):
    lon: float
    lat: float

class Hotel(BaseModel):
    id: str
    title: str
    description: str
    amenities: Dict[str, List[str]]
    location: Location
    highlights: List[str]
    local_tips: List[str]
    url: str
