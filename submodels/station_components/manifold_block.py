from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal


class Manifold_Block_Model(BaseModel):
    series: Literal["3", "5", "7"]
    piping_direction: Literal["1", "2"]
    wiring_type: Literal["S", "D"]
    ab_port_size: Literal["00", "C2","C3","C4","C6","C8","C10", "C12",
                          "N1", "N3","N7","N9","N11","L4","L6","L8","L10","L12","LN3","LN7","LN9","LN11",
                          "B4","B6","B8","B10","B12","BN3","BN7","BN9","BN11"
    ]

    # Creating manifold block part number
    def part_number(self) -> str:
        # standard manifold block (SY#0M-2-##A-#)
        return f"SY{self.series}0M-2-{self.piping_direction}{self.wiring_type}A-{self.ab_port_size}"

    @model_validator(mode="after")
    def logical_checks(self):
        # Ensuring series to ab port size matches
        if self.series == "3" and self.ab_port_size not in ("C2","C3","C4","C6","N1", "N3","N7",
                                                            "L4","L6","LN3","LN7","B4","B6", "BN3","BN7"):
            raise ValueError(f"3000 Series is not compatible with the selected ab port size {self.ab_port_size}")
        if self.series == "5" and self.ab_port_size not in ("C4","C6","C8", "N3","N7","N9",
                                                            "L4","L6","L8", "LN7","LN9","B4","B6","B8", "BN7","BN9"):
            raise ValueError(f"5000 Series is not compatible with the selected ab port size {self.ab_port_size}")
        if self.series == "7" and self.ab_port_size not in ("C6","C8","C10","C12","N7","N9","N11",
                                                            "L6","L8","L10","L12","LN11","B6","B8", "B10","B12","BN11"):
            raise ValueError(f"7000 Series is not compatible with the selected ab port size {self.ab_port_size}")
        return self

# -- Testing -- Testing -- Testing -- Testing -- Testing -- Testing --
# test_data = {
#     "series": "3",
#     "piping_direction": "1",
#     "wiring_type": "S",
#     "ab_port_size": "C3",
# }

# try:
#     manifold_block_obj = Manifold_Block_Model(**test_data) #type: ignore
#     print(manifold_block_obj.part_number())
# except ValidationError as e:
#     for err in e.errors():
#         print(err["msg"])