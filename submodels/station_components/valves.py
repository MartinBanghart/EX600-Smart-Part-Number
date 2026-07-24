# to run model for testing in terminal
# --- run from root folder directory
# --- use command "python -m submodels.station_components.valves"
# --- don't add '.py' to end of model file or else won't work

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Literal

from utilities.config import YAML_DATA, ab_mixed_fitting_tables

class Valves_Model(BaseModel):
    # dropping any fields passed that are not declared in model
    model_config = {"extra": "ignore"}

    # --- Fields extracted from YAML entry ---
    symbol: str
    type: Literal["valve"]
    actuation: Literal["1", "2", "3", "4", "5", "A", "B", "C"]
    seal_type: Literal["", "0", "1"]
    pilot_type: Literal["", "R"]
    back_pressure_check: Literal["", "H"]
    pilot_valve: Literal["", "B", "K"]
    fitting_size: Literal[0, 1, 2, 3]
    solenoid_qty: Literal[1, 2]

    # --- Fields to be inherited from main model class instance ---
    series: Literal["3", "5", "7"]
    porting_type: Literal["10", "11", "12"]
    manual_override: Literal["", "D", "E", "F"]
    ab_port_size: str
    lt_surge_volt_sup: Literal["R", "U", "S", "Z", "NS", "NZ"]
    coil_type: Literal["", "T"]
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
    

    # Creating valve part number
    def part_number(self) -> str:
        return (
            f"SY{self.series}{self.actuation}0{self.seal_type}{self.pilot_type}{self.back_pressure_check}{self.pilot_valve}{self.coil_type}"
            f"-5{self.lt_surge_volt_sup}{self.manual_override}1"
        )

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
    
    # -------------- MODEL LOGIC --------------
    def model_logic(self):
        if self.actuation in ("A", "B", "C") and self.seal_type != "0":
            raise ValueError("Rubber seal type must be selected for 4 position dual 3 port actuation type")
        if self.back_pressure_check == "H" and self.seal_type != "0":
            raise ValueError("Rubber seal type must be selected for built-in back pressure check valve")
        if self.back_pressure_check == "H" and self.series == "7":
            raise ValueError("Back pressure check valve is not available for SY7000 series")
        if self.pilot_valve == "K" and self.seal_type != "1":
            raise ValueError("Metal seal type must be selected for high pressure pilot valve type")
        if self.lt_surge_volt_sup not in ('Z', 'NZ') and self.coil_type == "T":
            raise ValueError("Power saving circuit is only available with type 'Z' and 'NZ' light surge voltage suppressors")
        return self

# ----------------- TESTING -----------------
# test_data = {
#     "series": "3",
#     "type": "base_mounted_valve",
#     "desc": "2 POS SGL, RUBBER SEAL",
#     "actuation": "1",
#     "seal_type": "0",
#     "pilot_type": "",
#     "back_pressure_check": "",
#     "pilot_valve": "",
#     "fitting_size": 0,
#     "solenoid_qty": 1,
#     "x_option": False,
#     "lt_surge_volt_sup": "R",
#     "coil_type": "",
#     "manual_override": "D",
#     "ab_port_size": "11",
#     "porting_type": "10",
# }

# valve_obj = Base_Mounted_Valves_Model(**test_data)
# print("\n")

# print(valve_obj)
# print(valve_obj.valve_part_number())
# print("\n")
# print(valve_obj.manifold_block_part_number())
# print("\n")
# print(valve_obj.mix_mount_manifold_block_3000_5000_part_number())


# print("\n")
