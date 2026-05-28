# to run model for testing in terminal
# --- run from root folder directory
# --- use command "python -m submodels.port_block_assy"
# --- don't add '.py' to end of model file or else won't work

from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal
from utilities.config import YAML_DATA, port_block_tables

# Generic Formula for all port blocks: SY#0M-#-1A#-##
# #1) Series
# #2) PE port entry (either Internal Pilot, Internal Pilot/Built-In silencer, External Pilot)
# #3) 

class Port_Block_Assy_Model(BaseModel):
    series: Literal["3", "5", "7"]
    porting_type: Literal["10", "11", "12"]
    pilot_silencer_piping_type: Literal["", "S", "R", "V", "RV", "VP", "B", "BS", "BR"]
    pe_port_entry: Literal["U", "D", "B", "C", "E", "F", "G", "H", "J"]
    port_measurement_type: Literal['metric', 'imperial']
    fitting_direction: Literal['straight', "downward elbow", "upward elbow"]
    
    # Calculated Fields
    pe_port_size: Optional[Literal["","00", "C8", "C10", "C12", "N9", "N11", "N13"]] = None
    part_number_scheme: Optional[str] = None
    ab_port_fitting_piping_dir: Optional[str] = None
    x_pe_port_fitting_type: Optional[str] = None
    
    # determine which part number scheme to use for the cover assembly/port block assembly
    @model_validator(mode="after")
    def get_matching_scheme(self): #, schemes: dict[str, dict[str, list[str]]]) -> list[str]:
        schemes = port_block_tables["part_number_schemes"]
        matches = []

        for scheme_name, rules in schemes.items():
            is_match = True

            for field, allowed_values in rules.items():
                if allowed_values == [""]:
                    continue  # skip validation for this field

                model_value = getattr(self, field, None)

                if model_value not in allowed_values:
                    is_match = False
                    break

            if is_match:
                matches.append(scheme_name)

        
        # enforce mutually exclusive logic
        if len(matches) == 0:
            raise ValueError("No matching part number scheme found")
        elif len(matches) > 1:
            raise ValueError(f"Multiple matching schemes found: {matches}")

        # store as a single string
        self.part_number_scheme = matches[0]

        return self
    
    @model_validator(mode="after")
    def get_ab_port_fitting_piping_dir(self):
        if self.porting_type == "11":
            self.ab_port_fitting_piping_dir = ""
        elif self.porting_type == "10" and self.fitting_direction == "downward elbow":
            self.ab_port_fitting_piping_dir = ""
        elif self.porting_type == "10" and self.fitting_direction == "upward elbow":
            self.ab_port_fitting_piping_dir = "V"
        else:
            self.ab_port_fitting_piping_dir = ""
        
        return(self)
    
    @model_validator(mode="after")
    def get_x_pe_port_fitting_type(self):
        if self.series in ('3', '5') and self.port_measurement_type == 'metric':
            self.x_pe_port_fitting_type = ""
        elif self.series in ('7') and self.port_measurement_type == 'metric':
            self.x_pe_port_fitting_type = ""
        elif self.series in ('3', '5') and self.port_measurement_type == 'imperial':
            self.x_pe_port_fitting_type = "U"
        elif self.series in ('7') and self.port_measurement_type == 'imperial':
            self.x_pe_port_fitting_type = "U"
        else:
            self.x_pe_port_fitting_type = ""
        
        return(self)

    # cover assembly part number
    def part_number(self) -> str:
        # cover assembly 
        if self.part_number_scheme == "cover_assy":
            pn = f"SY{self.series}0M-4-1A"
            
        # silencer cover assembly
        if self.part_number_scheme == "silencer_cover_assy":
            pn = f"SY{self.series}0M-5-1A"
            
        # port block assembly (porting_type: 10,11 ; pe_port_entry: G,H,J ; fitting_direction: straight, downward elbow ;  )
        if self.part_number_scheme == "ext_port_block_assy":
            pn = f"SY{self.series}0M-6-1AR{self.ab_port_fitting_piping_dir}-00{self.x_pe_port_fitting_type}"
            
        return pn

# -- Testing -- Testing -- Testing -- Testing -- Testing -- Testing --

test_data = {
    "series": "5",
    "porting_type": "10",
    "pe_port_entry": "G",
    "pilot_silencer_piping_type": "S",
    "port_measurement_type": "metric",
    "fitting_direction": "upward elbow"
}

try:
    port_block_obj = Port_Block_Assy_Model(**test_data) #type: ignore
    print(port_block_obj.part_number())
except ValidationError as e:
    for err in e.errors():
        print(err["msg"])