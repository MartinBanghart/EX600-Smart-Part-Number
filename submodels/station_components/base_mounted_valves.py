from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Literal


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

    # In YAML file any empty string or not used values will be set to ~ which is None type
    # To make concatenation easier, these will be converted to empty strings in the model
    @field_validator("seal_type", "pilot_type", "pilot_valve", "back_pressure_check", mode="before")
    def convert_yaml_none_to_strings(cls, v):
        if v is None:
            return ""
        return str(v)

    # ------------------------------- MODEL VALIDATOR 'AFTER' -------------------------------------
    @model_validator(mode="after")
    def get_manifold_block_wiring_type(self):
        if self.solenoid_qty == 1:      # valve is single solenoid
            self.manifold_block_wiring_type = 'S'
        elif self.solenoid_qty == 2:    # valve is double solenoid
            self.manifold_block_wiring_type = 'D' 
        elif self.solenoid_qty == 0:    # blanking plate --> assume double wired since customer could swap for double solenoid valve
            self.manifold_block_wiring_type = 'D'
        return self

    # Creating valve part number
    def valve_part_number(self) -> str:
        return (
            f"SY{self.series}{self.actuation}0{self.seal_type}{self.pilot_type}{self.back_pressure_check}{self.pilot_valve}{self.coil_type}"
            f"-5{self.lt_surge_volt_sup}{self.manual_override}1"
        )

    # Creating manifold block part number
    # def type_10_11_manifold_block_part_number(self) -> str:
    #     # standard manifold block (SY#0M-2-##A-#)
    #     return(
    #         f"SY{self.series}0M"
    #         f"-2"
    #         f"-{self.}"
    #         f"-2"
    #     )


# ----------------- TESTING -----------------
test_data = {
    "series": "3",
    "type": "base_mounted_valve",
    "desc": "2 POS SGL, RUBBER SEAL",
    "actuation": "1",
    "seal_type": "0",
    "pilot_type": None,
    "back_pressure_check": None,
    "pilot_valve": None,
    "fitting_size": 0,
    "solenoid_qty": 1,
    "x_option": False,
    "lt_surge_volt_sup": "R",
    "coil_type": "",
    "manual_override": "D",
    "ab_port_size": "C9",
    "porting_type": "10"
}

valve_obj = Base_Mounted_Valves_Model(**test_data)
print("\n")

print(valve_obj)
print(valve_obj.valve_part_number())

# print("\n")
