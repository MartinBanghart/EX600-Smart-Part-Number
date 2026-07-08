from pydantic import BaseModel, ConfigDict, field_validator, model_validator, ValidationError
from typing import Optional, Literal

from utilities.config import YAML_DATA, ab_mixed_fitting_tables

class Blanking_Plate_Assy_Model(BaseModel):
    # dropping any fields passed that are not declared in model
    model_config = ConfigDict(extra="ignore")
    # --- Fields extracted from YAML entry ---
    symbol: str
    type: Literal["blanking_plate"]
    actuation: Literal[""]
    seal_type: Literal["", "0", "1"]
    pilot_type: Literal["", "R"]
    back_pressure_check: Literal["", "H"]
    pilot_valve: Literal["", "B", "K"]
    fitting_size: Literal[0, 1, 2, 3]
    solenoid_qty: Literal[0]
    
    # --- Fields to be inherited from main model class instance ---
    series: Literal["3", "5", "7"]
    porting_type: Literal["10", "11", "12"]
    ab_port_size: str
    number_of_stations: int
    
    # --- Fields Determined from inherited fields above ---
    manifold_block_wiring_type: str = ""
    
    # --- Calculated Part Numbers
    manifold_block_part_number: Optional[str] = None
    
    # --- Retrieved from YAML_DATA fields
    ab_port_size_hto: Optional[str] = None
    
    # ------------------------------- MODEL VALIDATOR 'AFTER' -------------------------------------
    @model_validator(mode="after")
    def run_all_postprocessing_and_logic(self):
        # --- computed fields
        self.get_manifold_block_wiring_type()
        self.get_ab_port_size_hto()
        self.get_manifold_part_number()
        # --- logic check
        self.model_logic()
        return self

    def get_manifold_block_wiring_type(self):
        if self.solenoid_qty == 1:  # valve is single solenoid
            self.manifold_block_wiring_type = "S"
        elif self.solenoid_qty == 2:  # valve is double solenoid
            self.manifold_block_wiring_type = "D"
        elif (self.solenoid_qty == 0):  # blanking plate --> assume double wired since customer could swap for double solenoid valve
            self.manifold_block_wiring_type = "D"
        return self
    
    # grabbing fitting_direction and port_measurement_type for the specific ab_port_size_symbol in yaml_data
    def get_ab_port_size_hto(self):
        data_dict = YAML_DATA["ab_port_size_symbols"][self.ab_port_size]
        size = data_dict["size"]
        
        if size in ("CM", "LM", "BM", "NM", "NLM", "NBM"):
            self.ab_port_size_hto = ab_mixed_fitting_tables["series"][self.series]["porting"][self.porting_type][size][self.fitting_size]
        else:
            self.ab_port_size_hto = size
            
        return self
    
        # Creating manifold block part number
    def standard_manifold_block_part_number(self) -> str:
        if self.porting_type in ("10", "11"):
            piping_direction = "1"
        elif self.porting_type in ("12"):
            piping_direction = "2"

        # standard manifold block (SY#0M-2-##A-#)
        return(f"SY{self.series}0M-2-{piping_direction}{self.manifold_block_wiring_type}A-{self.ab_port_size_hto}")

    def mix_mount_manifold_block_3000_5000_part_number(self) -> str:
        # mixed mounting 3000/5000 manifold block (SY50M-2-##A-#) - used for bottom ported (type 11) 3000 series
        if self.porting_type in ("10", "11"):
            piping_direction = "3"
        elif self.porting_type in ("12"):
            piping_direction = "4"
        # standard manifold block (SY50M-2-##A-#)
        return(f"SY50M-2-{piping_direction}{self.manifold_block_wiring_type}A-{self.ab_port_size_hto}")
    
    # setting manifold_block_part_number field
    # --- if bottom ported 3000 series, it must use SY5000 mixed mounting block, otherwise its standard manifold block
    def get_manifold_part_number(self):
        if self.series == "3" and self.porting_type == "11":
            self.manifold_block_part_number = self.mix_mount_manifold_block_3000_5000_part_number()
        else:
            self.manifold_block_part_number = self.standard_manifold_block_part_number()
        
        return self
    
    def part_number(self) -> str:
        if self.symbol == 'WH':
            return('SY30M-150-1A')
        elif self.symbol == 'WI':
            return('SY30M-150-1A-10')
        elif self.symbol == 'WJ':
            return('SY30M-150-1A-1')
        elif self.symbol == 'WK':
            return('SY30M-150-1A-1-10')
        elif self.symbol == 'WL':
            return('SY30M-150-1A-2')
        elif self.symbol == 'WM':
            return('SY30M-150-1A-2-10')
        else:
            # standard blanking plate (SY#0M-26-1A-#)
            return f"SY{self.series}0M-26-1A"
    
    # -------------- MODEL LOGIC --------------
    def model_logic(self):
        return self