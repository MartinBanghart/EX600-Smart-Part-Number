# to run model for testing in terminal
# --- run from root folder directory
# --- use command "python -m submodels.u_sup_exh_block_assy"
# --- don't add '.py' to end of model file or else won't work

from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal
from utilities.config import YAML_DATA, u_side_sup_exh_tables


class Sup_Exh_Block_Assy_Model(BaseModel):
    sup_exh_porting_dir_and_cover_assy: str
    series: Literal["3", "5", "7"]
    pilot_silencer_piping_type: Literal["", "S", "R", "V", "RV", "VP", "B", "BS", "BR"]
    porting_type: Literal["10", "11", "12"]
    port_measurement_type: Literal["metric", "imperial"]
    mounting_and_nameplate: str
    fitting_direction: str
    # --- Calculated fields
    u_pe_port_size: Optional[str] = None
    d_pe_port_size: Optional[str] = None
    mounting: Optional[Literal["", "D0"]] = None
    
    # --- determining pe_port_size field
    @model_validator(mode="after")
    def get_pe_port_size(self):
        pe_port_table = u_side_sup_exh_tables["pe_port_table"]

        # find matching entry
        for key, entry in pe_port_table.items():
            if (
                self.series in entry["series"]
                and self.porting_type in entry["porting_type"]
                and (entry["measurement"] == "" or entry["measurement"] == self.port_measurement_type)
                and (entry["type"] == self.fitting_direction)
            ):
                # check sup_exh_porting_dir_and_cover_assy_symbols field --> u_side_fittings and d_side_fittings
                # -- based on pe_port_entry, d or u side will be plugged
                data = YAML_DATA["sup_exh_porting_dir_and_cover_assy_symbols"][self.sup_exh_porting_dir_and_cover_assy]
                
                if data["u_side_fittings"] == False:
                    self.u_pe_port_size = "00"
                else:
                    self.u_pe_port_size = key
                    
                if data["d_side_fittings"] == False:
                    self.d_pe_port_size = "00"
                else:
                    self.d_pe_port_size = key    
                    
                return self

        raise ValueError("No valid pe_port_size found for given inputs")
    
    # --- determining mounting field
    @model_validator(mode="after")
    def get_mounting(self):
        mounting_style = YAML_DATA["mounting_and_nameplate_symbols"][self.mounting_and_nameplate]['mounting']
        
        if mounting_style == 'direct':
            self.mounting = ""
        else:
            self.mounting = "D0"
        
        return self
    
    # --- logical checks for part number
    @model_validator(mode="after")
    def logical_checks(self):
        # Ensuring series to ab port size matches
        if self.series == "3" and self.u_pe_port_size not in ("C8","N9","L8","LN9","B8","BN9","00"):
            raise ValueError(f"3000 Series is not compatible with the selected pe port size {self.u_pe_port_size}")
        if self.series == "5" and self.u_pe_port_size not in ("C10","N11","N9","L10","LN11","B10","BN11","00"):
            raise ValueError(f"5000 Series is not compatible with the selected pe port size {self.u_pe_port_size}")
        if self.series == "7" and self.u_pe_port_size not in ("C12","N13","L12","LN13","B12","BN13"):
            raise ValueError(f"7000 Series is not compatible with the selected pe port size {self.u_pe_port_size}")
        
        # Bottom ported (type: 11), cannot have din rail mounting
        if self.porting_type == "11" and self.mounting != '':
            raise ValueError("Bottom ported manifolds cannot have din rail mounting")
        return self
    
    # u side sup/exh block assembly part number
    def u_side_part_number(self) -> str:
        # standard u side supply exhaust block (SY#0M-3-1A#-#-#)
        mounting_section = f"-{self.mounting}" if self.mounting else ""
        return f"SY{self.series}0M-3-1A{self.pilot_silencer_piping_type}-{self.u_pe_port_size}{mounting_section}"

    # d side sup/exh block assembly part number
    def d_side_part_number(self) -> str:
        # standard u side supply exhaust block (SY#0M-1-1A#-#-#)
        mounting_section = f"-{self.mounting}" if self.mounting else ""
        return f"SY{self.series}0M-1-1A{self.pilot_silencer_piping_type}-{self.d_pe_port_size}{mounting_section}"

# -- Testing -- Testing -- Testing -- Testing -- Testing -- Testing --

# Example: Overall Smart Part Number Sup/Exh Porting Direction and Cover Assembly calls out
# --- "A"
data = YAML_DATA['sup_exh_porting_dir_and_cover_assy_symbols']['M']

test_data = {
    "sup_exh_porting_dir_and_cover_assy":YAML_DATA['sup_exh_porting_dir_and_cover_assy_symbols']['M'],
    "series": "5",
    "pilot_silencer_piping_type": data["pilot_silencer_piping_type"],
    "mounting_and_nameplate": "AA",
    "porting_type": "12",
    "port_measurement_type": "metric",
    "fitting_direction": "straight"
}

try:
    sup_exh_block_obj = Sup_Exh_Block_Assy_Model(**test_data) #type: ignore
    print(sup_exh_block_obj.u_side_part_number())
    print(sup_exh_block_obj.d_side_part_number())
    # print(sup_exh_block_obj.pe_port_size)
except ValidationError as e:
    for err in e.errors():
        print(err["msg"])