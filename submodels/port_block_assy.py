from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal


class Port_Block_Assy_Model(BaseModel):
    series: Literal["3", "5", "7"]
    type: str
    pilot_silencer_piping_type: Literal["", "S", "R","V", "RV", "VP", "B", "BS", "BR"]
    pe_port_size: Literal["00", "C8","C10", "C12",
                        "N9","N11","N13"]
    mounting: Literal["", "D0"]


    @field_validator("type", mode="before")
    def get_type(cls, v):
    
        return(v)
    
    # Creating manifold block part number
    def part_number(self) -> str:
        # standard manifold block (SY#0M-2-##A-#)
        mounting_section = f"-{self.mounting}" if self.mounting else ""
        return f"SY{self.series}0M-3-1A{self.pilot_silencer_piping_type}-{self.pe_port_size}{mounting_section}"