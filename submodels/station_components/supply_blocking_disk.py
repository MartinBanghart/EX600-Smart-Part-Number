from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal

class Supply_Blocking_Disk_Model(BaseModel):
    symbol: Literal['X', 'Y', 'Z']
    series: Literal["3", "5", "7"]
    # --- Calculated fields
    
    # --- Calculated Part Numbers
    manifold_block_part_number: Optional[str] = None
    
    # --- Retrieved from YAML_DATA fields
    ab_port_size_hto: Optional[str] = None
    
    @model_validator(mode="after")
    def run_all_postprocessing_and_logic(self):
        # --- computed fields
        self.get_ab_port_size_hto()
        self.get_manifold_part_number()
        # --- logic check
        self.model_logic()
        return self
    
    # grabbing fitting_direction and port_measurement_type for the specific ab_port_size_symbol in yaml_data
    def get_ab_port_size_hto(self):
        self.ab_port_size_hto = "-"
        return self
    
    # setting manifold_block_part_number field
    # --- supply blocking disk does not require a manifold block as it does not exist in or on its own manifold station
    def get_manifold_part_number(self):
        self.manifold_block_part_number = "-"
        return self

    # generating the supply blocking disk part number
    def part_number(self) -> str:
        # SUP (P) blocking disk assembly (SY#0M-40-1A)
        if self.symbol == 'X':
            return(f"SY{self.series}0M-26-1A")
        # EXH (E) blocking disk assembly (SY#0M-40-2A)
        elif self.symbol == 'Z':
            return(f"SY{self.series}0M-26-2A")
        # SUP/EXH (P/E) blocking disk assembly (SY#0M-40-2A)
        else: # self.symbol == 'Y'
            return(f"SY{self.series}0M-26-1A , SY{self.series}0M-26-2A")

    # -------------- MODEL LOGIC --------------
    def model_logic(self):
        return self
        