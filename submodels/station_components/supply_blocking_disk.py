from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal

class Supply_Blocking_Disk_Model(BaseModel):
    symbol: Literal['X', 'Y', 'Z']
    series: Literal["3", "5", "7"]
    # --- Calculated fields

    def supply_block_disk_part_number(self) -> str:
        # SUP (P) blocking disk assembly (SY#0M-40-1A)
        if self.symbol == 'X':
            return(f"SY{self.series}0M-26-1A")
        # EXH (E) blocking disk assembly (SY#0M-40-2A)
        elif self.symbol == 'Z':
            return(f"SY{self.series}0M-26-2A")
        # SUP/EXH (P/E) blocking disk assembly (SY#0M-40-2A)
        else:
            return(f"SY{self.series}0M-26-2A")