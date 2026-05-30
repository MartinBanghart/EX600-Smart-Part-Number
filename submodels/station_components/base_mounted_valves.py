# to run model for testing in terminal
# --- run from root folder directory
# --- use command "python -m submodels.station_components.base_mounted_valves"
# --- don't add '.py' to end of model file or else won't work

from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Literal

from utilities.config import YAML_DATA

class Base_Mounted_Valves_Model(BaseModel):
    # dropping any fields passed that are not declared in model
    model_config = {"extra": "ignore"}

    # --- Fields extracted from YAML entry ---
    type: Literal["base_mounted_valve"]
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

    # --- Fields Determined from inherited fields above ---
    manifold_block_wiring_type: str = ""

    # --- Retrieved from YAML_DATA fields
    ab_port_size_hto: Optional[str] = None

    # ------------------------------- MODEL VALIDATOR 'AFTER' -------------------------------------
    @model_validator(mode="after")
    def run_all_postprocessing_and_logic(self):
        # --- computed fields
        self.get_manifold_block_wiring_type()
        self.get_ab_port_size_hto()
        # --- logic check
        # self.model_logic()
        return self

    def get_manifold_block_wiring_type(self):
        if self.solenoid_qty == 1:  # valve is single solenoid
            self.manifold_block_wiring_type = "S"
        elif self.solenoid_qty == 2:  # valve is double solenoid
            self.manifold_block_wiring_type = "D"
        elif (
            self.solenoid_qty == 0
        ):  # blanking plate --> assume double wired since customer could swap for double solenoid valve
            self.manifold_block_wiring_type = "D"
        return self
    
    # grabbing fitting_direction and port_measurement_type for the specific ab_port_size_symbol in yaml_data
    def get_ab_port_size_hto(self):
        data_dict = YAML_DATA["ab_port_size_symbols"][self.ab_port_size]
        self.ab_port_size_hto = data_dict["size"]
        return self
    
    # #  --- Overall Logic for Main Model ---
    # def model_logic(self):
    #     # 
    #     if :
    #         raise ValueError("")
    #     # 
    #     if :
    #         raise ValueError("")
        
        
        return self

    # Creating valve part number
    def valve_part_number(self) -> str:
        return (
            f"SY{self.series}{self.actuation}0{self.seal_type}{self.pilot_type}{self.back_pressure_check}{self.pilot_valve}{self.coil_type}"
            f"-5{self.lt_surge_volt_sup}{self.manual_override}1"
        )

    # Creating manifold block part number
    def manifold_block_part_number(self) -> str:
        if self.porting_type in ("10", "11"):
            piping_direction = "1"
        elif self.porting_type in ("12"):
            piping_direction = "2"

        # standard manifold block (SY#0M-2-##A-#)
        return(f"SY{self.series}0M-2-{piping_direction}{self.manifold_block_wiring_type}A-{self.ab_port_size_hto}"
        )

    def mix_mount_manifold_block_3000_5000_part_number(self) -> str:
        # mixed mounting 3000/5000 manifold block (SY50M-2-##A-#) - used for bottom ported (type 11) 3000 series
        if self.porting_type in ("10", "11"):
            piping_direction = "3"
        elif self.porting_type in ("12"):
            piping_direction = "4"
        # standard manifold block (SY50M-2-##A-#)
        return(f"SY50M-2-{piping_direction}{self.manifold_block_wiring_type}A-{self.ab_port_size_hto}")


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
