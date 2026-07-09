from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Optional, Literal
from utilities.config import YAML_DATA


class SI_Unit_Model(BaseModel):
    symbol: str
    si_unit_polarity: Literal["", "NPN", "PNP"]
    # --- Calculated fields

    def part_number(self) -> str:
        
        protocol = YAML_DATA['si_unit_symbols'][self.symbol]['protocol']
        
        io_unit_map = {
        "PR1A": {"protocol": "PROFIBUS DP", "output_type": "PNP",},
        "PR2A": {"protocol": "PROFIBUS DP", "output_type": "NPN",},
        "DN1A": {"protocol": "DeviceNet", "output_type": "PNP",},
        "DN2A": {"protocol": "DeviceNet", "output_type": "NPN",},
        "MJ1": { "protocol": "CC-Link", "output_type": "PNP",},
        "MJ2": { "protocol": "CC-Link", "output_type": "NPN",},
        "EN7": {"protocol": "EtherNet IP", "output_type": "PNP",},
        "EN8": {"protocol": "EtherNet IP", "output_type": "NPN",},
        "EC3": {"protocol": "EtherCAT", "output_type": "PNP",},
        "EC4": {"protocol": "EtherCAT", "output_type": "NPN",},
        "PN3": {"protocol": "PROFINET (IO-Link)", "output_type": "PNP",},
        "PN4": {"protocol": "PROFINET (IO-Link)", "output_type": "NPN",},
        "PN31": {"protocol": "PROFINET (OPC UA, IO-Link)", "output_type": "PNP",},}
        
        
        matching_symbol = next(
            (
                symbol
                for symbol, data in io_unit_map.items()
                if data["protocol"] == protocol
                and data["output_type"] == self.si_unit_polarity
            ),
            None,
        )

        # if no matching_symbol is found
        if self.symbol in (None, "0"):
            return ""



        return f"EX600-S{matching_symbol}"