# schemas.py
from pydantic import BaseModel, model_validator, field_validator
from typing import Optional
from state import (
    ALLOWED_CITIES,
    DISTRICTS_BY_CITY,
    AVAILABLE_DATES,
    VALIDATION_BOUNDS,
    DEFAULTS
)


class PredictionRequest(BaseModel):
    city: str
    district: str
    area_m2: float

    bedrooms: Optional[int] = None
    floor: Optional[int] = None
    year: Optional[int] = None
    month: Optional[int] = None

    @model_validator(mode="after")
    def validate_location(self):
        if self.city not in ALLOWED_CITIES:
            raise ValueError(f"City '{self.city}' is not supported by the model")

        allowed_districts = DISTRICTS_BY_CITY.get(self.city)
        if not allowed_districts or self.district not in allowed_districts:
            raise ValueError(f"District '{self.district}' is not supported for city '{self.city}'")
        return self

    @field_validator("area_m2")
    @classmethod
    def validate_area_m2(cls, v):
        bounds = VALIDATION_BOUNDS["area_m2"]
        if not bounds["min"] <= v <= bounds["max"]:
            raise ValueError(f"area_m2 must be between {bounds['min']} and {bounds['max']}")
        return v

    @field_validator("bedrooms")
    @classmethod
    def validate_bedrooms(cls, v):
        if v is None:
            return v

        bounds = VALIDATION_BOUNDS["bedrooms"]
        if not bounds["min"] <= v <= bounds["max"]:
            raise ValueError(f"bedrooms must be between {bounds['min']} and {bounds['max']}")
        return v

    @field_validator("floor")
    @classmethod
    def validate_floor(cls, v):
        if v is None:
            return v

        bounds = VALIDATION_BOUNDS["floor"]
        if not bounds["min"] <= v <= bounds["max"]:
            raise ValueError(f"floor must be between {bounds['min']} and {bounds['max']}")
        return v

    @model_validator(mode="after")
    def validate_year_month(self):
        # Both missing → allowed (backend may default)
        if self.year is None and self.month is None:
            return self

        # Month without year → invalid
        if self.year is None and self.month is not None:
            raise ValueError("Month cannot be provided without year")

        # Year provided, month omitted → OK
        if self.year is not None and self.month is None:
            if self.year not in AVAILABLE_DATES:
                raise ValueError(f"Year '{self.year}' is not supported by the model")
            return self

        # Year not supported
        allowed_months = AVAILABLE_DATES.get(self.year)
        if not allowed_months:
            raise ValueError(f"Year '{self.year}' is not supported by the model")

        # Month not valid for that year
        if self.month not in allowed_months:
            raise ValueError(f"Month '{self.month}' is not available for year '{self.year}'")

        return self

    @model_validator(mode="after")
    def apply_defaults(self):
        # Bedrooms
        if self.bedrooms is None:
            self.bedrooms = DEFAULTS["bedrooms"]

        # Floor
        if self.floor is None:
            self.floor = DEFAULTS["floor"]

        # Year / month (must stay coupled)
        if self.year is None:
            self.year = DEFAULTS["year"]

        if self.month is None:
            self.month = max(AVAILABLE_DATES[self.year])

        return self
