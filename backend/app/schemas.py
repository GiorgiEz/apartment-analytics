# schemas.py
from pydantic import BaseModel, model_validator, PrivateAttr
from typing import Optional
from backend.app.state import SALE_SCHEMA, RENT_SCHEMA


class PredictionRequest(BaseModel):
    transaction_type: str
    city: str
    district: str
    area_m2: float

    bedrooms: Optional[int] = None
    floor: Optional[int] = None
    year: Optional[int] = None
    month: Optional[int] = None

    # internal (not user input)
    _schema: dict = PrivateAttr()

    @model_validator(mode="after")
    def attach_schema(self):
        if self.transaction_type == "sale":
            self._schema = SALE_SCHEMA
        elif self.transaction_type == "rent":
            self._schema = RENT_SCHEMA
        else:
            raise ValueError("Invalid transaction_type")

        return self

    @model_validator(mode="before")
    @classmethod
    def apply_defaults(cls, data):
        t = data.get("transaction_type")

        if t == "sale":
            defaults = SALE_SCHEMA["defaults"]
        elif t == "rent":
            defaults = RENT_SCHEMA["defaults"]
        else:
            return data

        for key, value in defaults.items():
            if data.get(key) is None:
                data[key] = value

        return data

    @model_validator(mode="after")
    def validate_all(self):
        schema = self._schema

        # --- city
        if self.city not in schema["cities"]:
            raise ValueError(f"City '{self.city}' is not supported")

        # --- district
        if self.district not in schema["city_districts"].get(self.city, []):
            raise ValueError("Invalid district for city")

        # --- area
        limits = schema["area_m2"]
        if not (limits["hard_min"] <= self.area_m2 <= limits["hard_max"]):
            raise ValueError("Invalid area")

        # --- bedrooms
        b_limits = schema["bedrooms"]
        if not (b_limits["hard_min"] <= self.bedrooms <= b_limits["hard_max"]):
            raise ValueError("Invalid bedrooms")

        # --- floor
        f_limits = schema["floor"]
        if not (f_limits["hard_min"] <= self.floor <= f_limits["hard_max"]):
            raise ValueError("Invalid floor")

        # --- year/month
        years = schema["upload_date"]["years"]
        if self.year not in years:
            raise ValueError("Invalid year")

        valid_months = schema["upload_date"]["year_month_map"].get(str(self.year), [])
        if self.month not in valid_months:
            raise ValueError("Invalid month for year")

        return self