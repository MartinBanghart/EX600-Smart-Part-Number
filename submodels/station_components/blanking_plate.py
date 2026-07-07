from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal

class Blanking_Plate_Assy_Model(BaseModel):
    series: Literal["3", "5", "7"]
    # --- Calculated fields

    def standard_blanking_plate_part_number(self) -> str:
        # standard blanking plate (SY#0M-26-1A-#)
        return f"SY{self.series}0M-26-1A"