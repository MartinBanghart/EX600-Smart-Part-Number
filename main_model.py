# general dependencies
import pandas as pd

# pydantic dependencies
from pydantic import (BaseModel,field_validator,model_validator,Field,StringConstraints,ValidationError,)
from typing import Literal, Optional
from typing import Annotated

# general functions
from utilities.general_functions import TokenMapParser, parse_valve_callout

# submodels
from submodels.station_components.base_mounted_valves import Base_Mounted_Valves_Model
from submodels.mounting_and_nameplate import Mounting_And_Nameplate_Model

# Loading data
from utilities.config import YAML_DATA

# ------------------------------------------------------------------------------------
SY1_EX600_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SY", "length": 2},
    {"name": "series", "pattern": r"[357]", "length": 1},
    {"name": "EX600", "pattern": r"[6]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "si_unit", "pattern": r"(0|Q|N|V|E|D|F|G|W)", "length": 1},
    {"name": "endplate_type", "pattern": r"(2|3|4|5|6|7|8|9)?", "length": 1},
    {"name": "io_unit_1", "pattern": r"[A-Z1]?", "length": None},
    {"name": "io_unit_2", "pattern": r"[A-Z1]?", "length": None},
    {"name": "io_unit_3", "pattern": r"[A-Z1]?", "length": None},
    {"name": "io_unit_4", "pattern": r"[A-Z1]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "lt_surge_volt_sup_and_coil_type","pattern": r"(R|U|S|Z|T|V|M)","length": 1,},
    {"name": "manual_override", "pattern": r"(D|E|F)?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "valve_callout","pattern": r"(?:(?:[2-9]|1[0-9]|2[0-4])?(?:0[DS]|[A-W][A-W]|X|Y|Z))+","length": None,},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "sup_exh_porting_dir_and_cover_assy", "pattern": r"[A-Z]", "length": 1},
    {"name": "ab_port_size","pattern": r"(1[1-7]|2[1-5]|3[1-5]|4[1-5]|5[1-4]|6[1-4])","length": 2,},
    {"name": "mounting_and_nameplate", "pattern": r"[ABD](?:0|[A-X])?", "length": None},
]

# --------------------------------------------------
class SY1_EX600_MODEL(BaseModel):
    # ----- How to Order Information -----
    # -----------------------------------------------------
    prefix: Literal["SY"]
    series: Literal["3", "5", "7"]
    EX600: Literal["6"]
    # -
    si_unit: Literal["0", "Q", "N", "V", "E", "D", "F", "G", "W"]
    endplate_type: Literal["", "2", "3", "4", "5", "6", "7", "8", "9"]
    io_unit_1: Annotated[str, StringConstraints(min_length=1, max_length=1, pattern=r"[A-Z1]")]
    io_unit_2: Annotated[str, StringConstraints(min_length=1, max_length=1, pattern=r"[A-Z1]")]
    io_unit_3: Annotated[str, StringConstraints(min_length=1, max_length=1, pattern=r"[A-Z1]")]
    io_unit_4: Annotated[str, StringConstraints(min_length=1, max_length=1, pattern=r"[A-Z1]")]
    # -
    lt_surge_volt_sup_and_coil_type: Literal["R", "U", "S", "Z", "T", "V", "W", "M"]  # M is for no valves
    manual_override: Literal["", "D", "E", "F"]
    # -
    valve_callout: Annotated[str,StringConstraints(min_length=2,max_length=19,pattern=r"(?:(?:[2-9]|1[0-9]|2[0-4])?(?:0[DS]|[A-W][A-W]|X|Y|Z))+",),]
    # -
    sup_exh_porting_dir_and_cover_assy: Annotated[str, StringConstraints(min_length=1, max_length=1, pattern=r"[A-Z]")]
    ab_port_size: Annotated[str,StringConstraints(min_length=2,max_length=2,pattern=r"(1[1-7]|2[1-5]|3[1-5]|4[1-5]|5[1-4]|6[1-4])",),]
    mounting_and_nameplate: Annotated[str,StringConstraints(min_length=0, max_length=2, pattern=r"(?:[ABD](?:0|[A-X]))?"),]

    # --- Fields determined from standard fields above  ---
    porting_type: Optional[Literal["10", "11", "12"]] = None
    pe_port_entry: Optional[Literal["U", "D", "B", "C", "E", "F"]] = None

    lt_surge_volt_sup: Optional[Literal["R", "U", "S", "Z", "NS", "NZ"]] = None
    coil_type: Optional[Literal["", "T"]] = None
    number_of_stations: int | None = None
    
    # --- Fields determined from standard fields and related to valves
    parsed_valves: list = Field(default_factory=list)
    valves: list = Field(default_factory=list)

    # --- Submodels- not a part of How-To-Order fields ---
    mounting: Mounting_And_Nameplate_Model | None = None

    # -----------------------------------------------------
    @field_validator("valve_callout", mode="after")
    def validate_and_parse_valve_callout(cls, v):
        try:
            parse_valve_callout(v, valid_symbols=set(YAML_DATA["valve_symbols"].keys()))
        except ValueError as e:
            raise ValueError(f"Invalid valve callout: {e}")

        return v

    def build_part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}{self.EX600}"
            f"-{self.si_unit}{self.endplate_type}{self.io_unit_1}{self.io_unit_2}{self.io_unit_3}{self.io_unit_4}"
            f"-{self.lt_surge_volt_sup_and_coil_type}{self.manual_override}"
            f"-{self.valve_callout}"
            f"-{self.sup_exh_porting_dir_and_cover_assy}{self.ab_port_size}{self.mounting_and_nameplate}"
        )

    # ----- SUB MODELS -----
    @model_validator(mode="after")
    def run_all_postprocessing_and_logic(self):
        # --- computed fields
        self._set_porting_type_and_pe_port_entry()
        self._set_lt_surge_volt_sup_and_coil_type()
        self._compute_parsed_valves_and_number_of_stations()
        # --- logic check
        self.main_model_logic()
        # --- subcomponents
        self.valves = self.attach_valve_models()
        # self._build_submodels()
        return self

    # breaking down sup_exh_porting_dir_and_cover_assy from HTO to get two fields: porting_type + pe_port_entry
    def _set_porting_type_and_pe_port_entry(self):
        data_dict = YAML_DATA["sup_exh_porting_dir_and_cover_assy_symbols"][self.sup_exh_porting_dir_and_cover_assy]
        self.porting_type = data_dict["porting_type"]
        self.pe_port_entry = data_dict["pe_port_entry"]

    # breaking down lt_surge_volt_sup_and_coil_type from HTO to get two fields: lt_surge_volt_sup + coil_type
    def _set_lt_surge_volt_sup_and_coil_type(self):
        data_dict = YAML_DATA["lt_surge_volt_sup_and_coil_type_symbols"][self.lt_surge_volt_sup_and_coil_type]
        self.lt_surge_volt_sup = data_dict["lt_surge_volt_sup"]
        self.coil_type = data_dict["coil_type"]

    # --- computed values ---
    def _compute_parsed_valves_and_number_of_stations(self):
        self.parsed_valves = parse_valve_callout(self.valve_callout, valid_symbols=set(YAML_DATA["valve_symbols"].keys()))
        self.number_of_stations = sum(int(ele["qty"]) for ele in self.parsed_valves)
        return self

    def _build_submodels(self):
        self.mounting = Mounting_And_Nameplate_Model(
            symbol=self.mounting_and_nameplate, parent_series=self.series
        )
        # self.valves = Base_Mounted_Valves_Model(
        #     lt_surge_volt_sup_and_coil_type=self.lt_surge_volt_sup_and_coil_type,
        #     manual_override = self.manual_override,
        #     ab_port_size=self.ab_port_size
        # )

        return self

    def attach_valve_models(self):

        VALVE_TYPE_REGISTRY = {
            "base_mounted_valve": Base_Mounted_Valves_Model,
            # "blanking_plate": Blanking_Plate_Model,
            # "X323_option": X323_Valve_Model,
        }

        enriched = []

        for item in self.parsed_valves:
            symbol = item["symbol"]

            # 1 --> Lookup YAML entry for this symbol
            yaml_entry = YAML_DATA["valve_symbols"].get(symbol)
            if yaml_entry is None:
                raise ValueError(f"No YAML entry found for valve symbol '{symbol}'")

            valve_type = yaml_entry["type"]

            # 2 --> lookup model class based on YAML type
            model_cls = VALVE_TYPE_REGISTRY.get(valve_type)
            if model_cls is None:
                raise ValueError(f"No model registered for valve type '{valve_type}'")

            # guarding against the possibility calculated fields were not populated and remain none
            if self.porting_type is None:
                raise ValueError("porting_type was not set before creating valve_model")
            if self.coil_type is None:
                raise ValueError("coil_type was not set before creating valve_model")
            if self.lt_surge_volt_sup is None:
                raise ValueError("lt_surge_volt_sup was not set before creating valve_model")

            # 3 --> instantiate the valve model
            valve_model = model_cls(
                type=valve_type,
                series=self.series,
                actuation=yaml_entry["actuation"],
                seal_type=yaml_entry["seal_type"],
                pilot_type=yaml_entry["pilot_type"],
                back_pressure_check=yaml_entry["back_pressure_check"],
                pilot_valve=yaml_entry["pilot_valve"],
                coil_type=self.coil_type,
                lt_surge_volt_sup=self.lt_surge_volt_sup,
                manual_override=self.manual_override,
                ab_port_size=self.ab_port_size,
                porting_type=self.porting_type,
                fitting_size=yaml_entry["fitting_size"],
                solenoid_qty=yaml_entry["solenoid_qty"],
            )

            # 4 --> append enriched element
            enriched.append(
                {
                    **item,
                    "model": valve_model.model_dump(),
                }
            )

        return enriched

    #  --- Overall Logic for Main Model ---
    def main_model_logic(self):
        # if no si unit is selected and endplate type is not Nil, raise error
        if self.si_unit == "0" and self.endplate_type != "":
            raise ValueError("No SI Unit was selected, endplate type must be nil")
        
        # if the valve callout section is too long (greater than 19 chars), raise error
        if len(self.valve_callout) > 19:
            raise ValueError("valve callout exceeds allowable maximum of 19 characters")
        
        
        return self


# ----------------------- TESTING - TESTING - TESTING - TESTING - TESTING - TESTING -----------------------

# 2AB2AT3AAX2AE5BB2AA
## -- ## PART NUMBERS FOR TESTING ## -- ##
part_number = "SY36-Q2AAAA-ZD-AA3AB2ACAD-A11D"
# part_number = "SY36-02AAAA-ZD-AA3AB2ACAD-A11D"  # mismatch: no si unit selected but endplate type does not match

model = SY1_EX600_TOKEN_MAP
token_map = SY1_EX600_TOKEN_MAP

print("\n --------------------------------------")

# tokens = {}
try:
    print(f"\nParsing:{part_number}\n")
    parser = TokenMapParser(token_map)
    tokens = parser.parse(part_number)
    # valve = model(**tokens) #type: ignore
    manifold = SY1_EX600_MODEL(**tokens)

    validator_df = pd.DataFrame(
        manifold.model_dump().items(), columns=["Field", "Value"]
    )
    print("\nPart number is valid.\n")
    print(validator_df)
    print("-------------")

# PyDantic Model is Throwing Error
except ValidationError as e:
    print("\nValidation error:")
    print("---------------------")
    for err in e.errors():
        message = err["msg"].removeprefix("Value error, ")
        print(f"{message}")

    if "tokens" in locals():
        print("\nParsed Tokens")
        print(pd.DataFrame([tokens]))

# Parser is Throwing Error
except ValueError as e:
    print(f"\nParse error: {e}")
    if "tokens" in locals():
        print("Partial Tokens Extracted")
        print(pd.DataFrame([tokens]).T)
    else:
        print("Parsing failed before any tokens could be generated.")
