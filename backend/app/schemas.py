from pydantic import BaseModel
from typing import Optional


class PredictionRequest(BaseModel):
    city: str
    district: str
    area_m2: float

    bedrooms: Optional[int] = None
    floor: Optional[int] = None
    year: Optional[int] = None
    month: Optional[int] = None
