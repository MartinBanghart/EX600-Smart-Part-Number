from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal


class U_Sup_Exh_Block_Assy_Model(BaseModel):
    series: Literal["3", "5", "7"]
    pilot_silencer_piping_type: Literal["", "S", "R","V", "RV", "VP", "B", "BS", "BR"]
    pe_port_size: Literal["00", "C8","C10", "C12",
                          "N9","N11","N13", 
                          "L8","L10","L12","LN9","LN11","LN13",
                          "B8","B10","B12","BN9","BN11","BN13"
    ]
    mounting: Literal["", "D0"]

    # Creating manifold block part number
    def part_number(self) -> str:
        # standard manifold block (SY#0M-2-##A-#)
        mounting_section = f"-{self.mounting}" if self.mounting else ""
        return f"SY{self.series}0M-3-1A{self.pilot_silencer_piping_type}-{self.pe_port_size}{mounting_section}"

    @model_validator(mode="after")
    def logical_checks(self):
        # Ensuring series to ab port size matches
        if self.series == "3" and self.pe_port_size not in ("C8","N9","L8","LN9","B8","BN9","00"):
            raise ValueError(f"3000 Series is not compatible with the selected pe port size {self.pe_port_size}")
        if self.series == "5" and self.pe_port_size not in ("C10","N11","N9","L10","LN11","B10","BN11","00"):
            raise ValueError(f"5000 Series is not compatible with the selected pe port size {self.pe_port_size}")
        if self.series == "7" and self.pe_port_size not in ("C12","N13","L12","LN13","B12","BN13"):
            raise ValueError(f"7000 Series is not compatible with the selected pe port size {self.pe_port_size}")
        return self

# -- Testing -- Testing -- Testing -- Testing -- Testing -- Testing --
test_data = {
    "series": "3",
    "pilot_silencer_piping_type": "S",
    "pe_port_size": "C12",
    "mounting": ""
}

try:
    sup_exh_block_obj = U_Sup_Exh_Block_Assy_Model(**test_data) #type: ignore
    print(sup_exh_block_obj.part_number())
except ValidationError as e:
    for err in e.errors():
        print(err["msg"])