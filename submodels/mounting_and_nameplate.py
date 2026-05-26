from pydantic import BaseModel, model_validator
from typing import Literal

from utilities.config import YAML_DATA


class Mounting_And_Nameplate_Model(BaseModel):
    symbol: str
    catalog_value: str | None = None
    mounting: str | None = None
    sta_length: int | None = (
        None  # due to A,B,D and A0, B0, D0 - not all values are ints intially
    )
    parent_series: str | None = None

    @model_validator(mode="after")
    def load_yaml_and_validate(self):
        if self.symbol not in YAML_DATA["mounting_and_nameplate_symbols"]:
            raise ValueError(f"Unknown mounting/nameplate symbol: {self.symbol}")

        entry = YAML_DATA["mounting_and_nameplate_symbols"][self.symbol]

        self.catalog_value = entry.get("catalog_value")
        self.mounting = entry.get("mounting")
        self.sta_length = entry.get("sta_length")

        # Example rule: series 7 cannot use mounting type "direct"
        # if self.parent_series == "7" and self.mounting == "direct":
        #     raise ValueError("Series 7 cannot use direct mounting")

        return self
