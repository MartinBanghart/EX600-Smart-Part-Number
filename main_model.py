# general dependencies
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# pydantic dependencies
from pydantic import (BaseModel, field_validator, model_validator, Field, StringConstraints,ValidationError)
from typing import Literal, Optional
from typing import Annotated

# general functions
from utilities.general_functions import TokenMapParser, parse_valve_callout

# submodels
from submodels.station_components.base_mounted_valves import Base_Mounted_Valves_Model
from submodels.station_components.blanking_plate import Blanking_Plate_Assy_Model
from submodels.station_components.manifold_base import Manifold_Base_Model
from submodels.station_components.supply_blocking_disk import Supply_Blocking_Disk_Model
from submodels.mounting_and_nameplate import Mounting_And_Nameplate_Model
from submodels.sup_exh_block_assy import Sup_Exh_Block_Assy_Model
from submodels.si_unit import SI_Unit_Model

# Loading data
from utilities.config import YAML_DATA

# ------------------------------------------------------------------------------------
SY1_EX600_TOKEN_MAP = [
    {"name": "prefix", "pattern": r"SY", "length": 2},
    {"name": "series", "pattern": r"[357]", "length": 1},
    {"name": "EX600", "pattern": r"[6]", "length": 1},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "si_unit", "pattern": r"(0|Q|N|V|E|D|F|G|W)", "length": 1},
    {"name": "endplate_type", "pattern": r"(2|3|4|5|6|7|8|9)?", "length": None},
    {"name": "io_unit_1", "pattern": r"[A-Z1]?", "length": None},
    {"name": "io_unit_2", "pattern": r"[A-Z1]?", "length": None},
    {"name": "io_unit_3", "pattern": r"[A-Z1]?", "length": None},
    {"name": "io_unit_4", "pattern": r"[A-Z1]?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "lt_surge_volt_sup_and_coil_type","pattern": r"(R|U|S|Z|T|V|W|M)","length": 1,},
    {"name": "manual_override", "pattern": r"(D|E|F)?", "length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "valve_callout","pattern": r"(?:(?:[1-9]|[12][0-9]|3[0-2])?(?:[A-W][A-W]|D|S|X|Y|Z))+","length": None},
    {"name": "separator", "pattern": r"-", "length": 1},
    {"name": "sup_exh_porting_dir_and_cover_assy", "pattern": r"[A-Z]", "length": 1},
    {"name": "ab_port_size","pattern": r"(1[1-7]|2[1-5]|3[1-5]|4[1-5]|5[1-4]|6[1-4]|7[1-6])","length": 2},
    {"name": "mounting_and_nameplate", "pattern": r"[ABD](?:0|[A-X])?", "length": None},
]
# ------------------------------------------------------------------------------------------
class SY1_EX600_MODEL(BaseModel):
    # ---------- How to Order Information ----------
    prefix: Literal["SY"]
    series: Literal["3", "5", "7"]
    EX600: Literal["6"]
    # -
    si_unit: Literal["0", "Q", "N", "V", "E", "D", "F", "G", "W"]
    endplate_type: Literal["", "2", "3", "4", "5", "6", "7", "8", "9"]
    io_unit_1: Annotated[str,StringConstraints(min_length=0,max_length=1,pattern=r"[A-Z1]?")]
    io_unit_2: Annotated[str,StringConstraints(min_length=0,max_length=1,pattern=r"[A-Z1]?")]
    io_unit_3: Annotated[str,StringConstraints(min_length=0,max_length=1,pattern=r"[A-Z1]?")]
    io_unit_4: Annotated[str,StringConstraints(min_length=0,max_length=1,pattern=r"[A-Z1]?")]
    # -
    lt_surge_volt_sup_and_coil_type: Literal["R", "U", "S", "Z", "T", "V", "W", "M"]  # M is for no valves
    manual_override: Literal["", "D", "E", "F"]
    # -
    valve_callout: Annotated[str,StringConstraints(min_length=2,max_length=19,pattern=r"(?:(?:[1-9]|[12][0-9]|3[0-2])?(?:[A-W][A-W]|D|S|X|Y|Z))+")]
    # -
    sup_exh_porting_dir_and_cover_assy: Annotated[str, StringConstraints(min_length=1, max_length=1, pattern=r"[A-Z]")]
    ab_port_size: Annotated[str,StringConstraints(min_length=2,max_length=2,pattern=r"(1[1-7]|2[1-5]|3[1-5]|4[1-5]|5[1-4]|6[1-4]|7[1-6])")]
    mounting_and_nameplate: Annotated[str,StringConstraints(min_length=0, max_length=2, pattern=r"(?:[ABD](?:0|[A-X]))?"),]

    # --- Fields determined from standard fields above  ---
    si_unit_polarity: Optional[Literal["", "NPN", "PNP"]] = None # recently took out NPN because technically can only be either PNP or NPN based on ednplate or none (if no si unit)
    valve_polarity: Optional[Literal["", "NPN", "PNP", "Non-Polar"]] = None
    
    porting_type: Optional[Literal["10", "11", "12"]] = None
    pe_port_entry: Optional[Literal["U", "D", "B", "C", "E", "F", "G", "H", "J"]] = None
    pilot_silencer_piping_type: Optional[Literal["", "S", "R", "V", "RV", "VP", "B", "BS", "BR"]] = None

    lt_surge_volt_sup: Optional[Literal["R", "U", "S", "Z", "NS", "NZ"]] = None
    coil_type: Optional[Literal["", "T"]] = None

    fitting_direction: Optional[Literal["straight", "upward elbow", "downward elbow"]] = None
    port_measurement_type: Optional[Literal['metric', 'imperial']] = None

    number_of_stations: int | None = None
    number_of_solenoids: int | None = None
    
    # --- Fields determined from standard fields and related to valves
    parsed_valves: list = Field(default_factory=list)
    valves: list | None = Field(default_factory=list)
    
    sup_exh_blocks: list | None = Field(default_factory=list)
    valve_plate: Optional[Literal["", "EX600-ZMV4"]] = None
    si_unit_pn: Optional[str] | None = None

    # --- Submodels- not a part of How-To-Order fields ---
    mounting: Mounting_And_Nameplate_Model | None = None

# ------------------------------------------------------------------------------------------
# -- field_validator that funs after model is intialized and does post-processing
# -- This creates a dictionary of each valve symbol with pertinent information from fields of the valve
# -- from the YAML Data
# ---> Dictionary format: parsed_valves = {"pos": -, "qty": -, "symbol": -, "fitting_size": -}
    @field_validator("valve_callout", mode="after")
    def validate_and_parse_valve_callout(cls, v):
        try:
            parse_valve_callout(v, valid_symbols=set(YAML_DATA["valve_symbols"].keys()))
        except ValueError as e:
            raise ValueError(f"Invalid valve callout: {e}")

        return v
# ------------------------------------------------------------------------------------------
    # ----- SUB MODELS -----
    @model_validator(mode="after")
    def run_all_postprocessing_and_logic(self):
        # --- computed fields ---
        self._set_si_unit_and_valve_polarities()
        self._set_porting_type_and_pe_port_entry_and_pilot_silencer_piping_type()
        self._set_lt_surge_volt_sup_and_coil_type()
        self._set_fitting_direction_and_port_measurement_type()
        self._compute_parsed_valves_and_num_of_stations_and_num_of_solenoids()
        # --- logic check ---
        self.main_model_logic()
        # --- subcomponents ---
        self.valves = self.attach_valve_models()
        self.sup_exh_blocks = self.attach_sup_exh_blocks()
        self.valve_plate = self.attach_valve_plate()
        self.si_unit_pn = self.attach_si_unit()
        # --- bill of materials (bom) ---
        self.bom()
        return self
# ------------------------------------------------------------------------------------------
    # -- Retrieving values from yaml_data for specific symbol values for model fields intialized as none --
    
    # breaking down sup_exh_porting_dir_and_cover_assy from HTO to get two fields: porting_type + pe_port_entry
    def _set_si_unit_and_valve_polarities(self):
        si_data_dict = YAML_DATA["endplate_type_symbols"][self.endplate_type]
        valve_data_dict = YAML_DATA["lt_surge_volt_sup_and_coil_type_symbols"][self.lt_surge_volt_sup_and_coil_type]
        self.si_unit_polarity = si_data_dict["polarity"]
        self.valve_polarity = valve_data_dict["polarity"]

    # breaking down sup_exh_porting_dir_and_cover_assy from HTO to get two fields: porting_type + pe_port_entry
    def _set_porting_type_and_pe_port_entry_and_pilot_silencer_piping_type(self):
        data_dict = YAML_DATA["sup_exh_porting_dir_and_cover_assy_symbols"][self.sup_exh_porting_dir_and_cover_assy]
        self.porting_type = data_dict["porting_type"]
        self.pe_port_entry = data_dict["pe_port_entry"]
        self.pilot_silencer_piping_type = data_dict["pilot_silencer_piping_type"]

    # breaking down lt_surge_volt_sup_and_coil_type from HTO to get two fields: lt_surge_volt_sup + coil_type
    def _set_lt_surge_volt_sup_and_coil_type(self):
        data_dict = YAML_DATA["lt_surge_volt_sup_and_coil_type_symbols"][self.lt_surge_volt_sup_and_coil_type]
        self.lt_surge_volt_sup = data_dict["lt_surge_volt_sup"]
        self.coil_type = data_dict["coil_type"]

    # grabbing fitting_direction and port_measurement_type for the specific ab_port_size_symbol in yaml_data
    def _set_fitting_direction_and_port_measurement_type(self):
        data_dict = YAML_DATA["ab_port_size_symbols"][self.ab_port_size]
        self.fitting_direction = data_dict["fitting_direction"]
        self.port_measurement_type = data_dict["measurement_system"]

    # --- computed values ---
    def _compute_parsed_valves_and_num_of_stations_and_num_of_solenoids(self):
        self.parsed_valves = parse_valve_callout(self.valve_callout, valid_symbols=set(YAML_DATA["valve_symbols"].keys()))
        self.number_of_stations = sum(int(ele["qty"]) for ele in self.parsed_valves)
        self.number_of_solenoids = sum(int(ele["qty"]) * int(YAML_DATA['valve_symbols'][ele["symbol"]]['solenoid_qty']) for ele in self.parsed_valves)
        return self
# ------------------------------------------------------------------------------------------
    def attach_valve_models(self):

        COMPONENT_TYPE_REGISTRY = {
            "base_mounted_valve": Base_Mounted_Valves_Model,
            "blanking_plate": Blanking_Plate_Assy_Model,
            "manifold_base": Manifold_Base_Model,
            "supply_blocking_disk": Supply_Blocking_Disk_Model,
            # "X323_option": X323_Valve_Model,
        }

        enriched = []

        for item in self.parsed_valves:
            symbol = item["symbol"]

            # 1 --> Lookup YAML entry for this symbol
            yaml_entry = YAML_DATA["valve_symbols"].get(symbol)
            if yaml_entry is None:
                raise ValueError(f"No YAML entry found for valve symbol '{symbol}'")

            component_type = yaml_entry["type"]

            # 2 --> lookup model class based on YAML type
            model_cls = COMPONENT_TYPE_REGISTRY.get(component_type)
            if model_cls is None:
                raise ValueError(f"No model registered for valve type '{component_type}'")

            # guarding against the possibility calculated fields were not populated and remain none
            if self.porting_type is None:
                raise ValueError("porting_type was not set before creating valve_model")
            if self.coil_type is None:
                raise ValueError("coil_type was not set before creating valve_model")
            if self.lt_surge_volt_sup is None:
                raise ValueError("lt_surge_volt_sup was not set before creating valve_model")

            # 3 --> instantiate the valve model
            component_model = model_cls(
                symbol = symbol,
                type=component_type,
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
                number_of_stations = self.number_of_stations
            )

            # 4 --> append enriched element
            enriched.append({**item, 
                                "valve_pn": component_model.part_number(), 
                                "ab_port_size": component_model.ab_port_size_hto,
                                "manifold_block_pn": component_model.manifold_block_part_number
                                })
            
        return enriched
# ------------------------------------------------------------------------------------------    
    def attach_sup_exh_blocks(self):
        
        # guarding against the possibility calculated fields were not populated and remain none
        if self.porting_type is None:
            raise ValueError("porting_type was not set before creating sup_exh_model")
        if self.pilot_silencer_piping_type is None:
            raise ValueError("pilot_silencer_piping_type was not set before creating sup_exh_model")
        if self.port_measurement_type is None:
            raise ValueError("port_measurement_type was not set before creating sup_exh_model")
        if self.fitting_direction is None:
            raise ValueError("fitting_direction was not set before creating sup_exh_model")
        if self.pe_port_entry is None:
            raise ValueError("pe_port_entry was not set before creating sup_exh_model")
        
        sup_exh_model = Sup_Exh_Block_Assy_Model(
            sup_exh_porting_dir_and_cover_assy = self.sup_exh_porting_dir_and_cover_assy,
            series = self.series,
            pilot_silencer_piping_type = self.pilot_silencer_piping_type,
            porting_type = self.porting_type,
            port_measurement_type = self.port_measurement_type,
            mounting_and_nameplate = self.mounting_and_nameplate,
            fitting_direction = self.fitting_direction, 
            pe_port_entry=self.pe_port_entry
        )
        
        sup_exh_blocks = [
            {'D-Side Sup/Exh' : sup_exh_model.d_side_part_number()},
            {'U-Side Sup/Exh' : sup_exh_model.u_side_part_number()}
            ]
        
        return sup_exh_blocks
# ------------------------------------------------------------------------------------------    
    # BOM element - simplified since there are only two options for a valve plate
    def attach_valve_plate(self):
        if self.si_unit == "0":
            return("")
        else:
            return("EX600-ZMV4")
# ------------------------------------------------------------------------------------------        
    # BOM element - uses SI_UNIT_Model to attach the SI unit part number via a method on the main model
    def attach_si_unit(self):
        
        if self.si_unit_polarity is None:
            raise ValueError("si_unit_polarity was not set before creating si_unit_model")
        
        si_unit_model = SI_Unit_Model(symbol = self.si_unit, si_unit_polarity = self.si_unit_polarity)
    
        si_unit_pn = si_unit_model.part_number()
        
        return si_unit_pn
# ------------------------------------------------------------------------------------------    
    # Method that generates the overall part number for the manifold + valve assembly (main_model)
    def part_number(self) -> str:
        return (
            f"{self.prefix}{self.series}{self.EX600}"
            f"-{self.si_unit}{self.endplate_type}{self.io_unit_1}{self.io_unit_2}{self.io_unit_3}{self.io_unit_4}"
            f"-{self.lt_surge_volt_sup_and_coil_type}{self.manual_override}"
            f"-{self.valve_callout}"
            f"-{self.sup_exh_porting_dir_and_cover_assy}{self.ab_port_size}{self.mounting_and_nameplate}"
        )
# ------------------------------------------------------------------------------------------
    # Method that creates a dataframe with the bill of materials for the assembly
    def bom(self) -> pd.DataFrame:
        
        # guards for calculated fields initialized as None
        if self.sup_exh_blocks is None:
            raise ValueError("sup_exh_blocks was not set before creating sup_exh_model")
        if self.valves is None:
            raise ValueError("valves was not set before creating main_model")
        if self.valve_plate is None:
            raise ValueError("valve_plate was not set properly")
        
        rows = []

        def add_row(
            position,
            part_number="-",
            symbol="-",
            manifold_block="-",
            ab_port_size="-",
        ):
            rows.append({
                "Position": position,
                "Symbol": symbol,
                "Part Number": part_number,
                "Manifold Block": manifold_block,
                "AB Port Size": ab_port_size,
            })

        # ------------------------------
        # Endplate
        add_row(
            "EX600 Endplate",
            part_number=(
                YAML_DATA["endplate_type_symbols"]
                .get(self.endplate_type, {})
                .get("endplate_part_number", "-")
            ),
            symbol=self.endplate_type or "-",
        )

        # ------------------------------
        # IO Unit Components
        add_row(
            "IO Unit 1",
            part_number=(
                YAML_DATA["io_unit_symbols"]
                .get(self.io_unit_1, {}) # adds condition with .get() to return none if io_unit_1 is not set
                .get("io_unit_part_number", "-")
            ),
            symbol=self.io_unit_1 or "-",
        )
        add_row(
            "IO Unit 2",
            part_number=(
                YAML_DATA["io_unit_symbols"]
                .get(self.io_unit_2, {})
                .get("io_unit_part_number", "-")
            ),
            symbol=self.io_unit_2 or "-",
        )
        add_row(
            "IO Unit 3",
            part_number=(
                YAML_DATA["io_unit_symbols"]
                .get(self.io_unit_3, {})
                .get("io_unit_part_number", "-")
            ),
            symbol=self.io_unit_3 or "-",
        )
        add_row(
            "IO Unit 4",
            part_number=(
                YAML_DATA["io_unit_symbols"]
                .get(self.io_unit_4, {})
                .get("io_unit_part_number", "-")
            ),
            symbol=self.io_unit_4 or "-",
        )
        
        # ------------------------------
        # SI Unit Component
        add_row("SI Unit", part_number=self.si_unit_pn or "-", symbol=self.si_unit or "-",)

        # ------------------------------
        # Valve Plate Component
        add_row("Valve Plate", self.valve_plate)
        
        # ------------------------------
        # D-Side Supply Exhaust Component
        add_row("D-Side Sup/Exh", part_number=self.sup_exh_blocks[0]["D-Side Sup/Exh"])

        # ------------------------------
        # Station Components
        station = 1

        for valve in self.valves:

            for _ in range(int(valve["qty"])):

                if valve["symbol"] in {"X", "Y", "Z"}:
                    position = "-"
                else:
                    position = f"STA-{station}"
                    station += 1

                add_row(
                    position=position,
                    symbol=valve["symbol"],
                    part_number=valve["valve_pn"],
                    manifold_block=valve["manifold_block_pn"],
                    ab_port_size=valve["ab_port_size"],
                )

        # ------------------------------
        # U-Side Supply Exhaust Component
        add_row("U-Side Sup/Exh", part_number=self.sup_exh_blocks[1]["U-Side Sup/Exh"])

        return pd.DataFrame(rows)
# ------------------------------------------------------------------------------------------          
    def bom_output_to_pdf(self):
        # ----- Method Description
        # --> Inputs: DataFrame (from bom() method)
        # --> Outputs: PDF file
        # - Allocates directory and creates one if none exist
        # ----------------------------
        
        # rel path --> update as necessary in future
        directory = r"outputs"
        # check if dir exists, otherwise make it
        os.makedirs(directory, exist_ok=True)

        # intialize the filename and creating filepath
        filename=f"{self.part_number()}_BOM.pdf"
        filepath = os.path.join(directory, filename)
        
        validator_df = self.get_tokens_df(full_report=False)
        bom_df = self.bom()

        fig, (ax1, ax2) = plt.subplots(
            2, 1,
            figsize=(8, 10),
            gridspec_kw={"height_ratios": [1.5, 3]}
        )

        for ax in (ax1, ax2):
            ax.axis("off")

        # Model main Tokens table
        validator_table = ax1.table(
            cellText=validator_df.values,
            colLabels=validator_df.columns,
            cellLoc="center",
            bbox=[0, 0, 1, 0.9] # x, y, width, height
        )
        validator_table.auto_set_font_size(False)
        validator_table.set_fontsize(9)

        ax1.set_title("Configuration", pad=5, y=.97, fontweight='bold')

        # BOM table
        bom_table = ax2.table(
            cellText=bom_df.values,
            colLabels=bom_df.columns,
            cellLoc="center",
            bbox=[0, 0, 1, 0.9]
        )
        bom_table.auto_set_font_size(False)
        bom_table.set_fontsize(9)

        ax2.set_title("Bill of Materials", pad=5, y=.97, fontweight='bold')

        plt.tight_layout()

        with PdfPages(filepath) as pdf:
            pdf.savefig(fig, bbox_inches="tight")

        plt.close(fig)

        
        return(self)
# ------------------------------------------------------------------------------------------
    # Method to return fields from the model in a DataFrame
    # -- Default is full_report = True, which is all fields (base and calculated)
    # -- full_report = False gives only the base fields from HTO
    def get_tokens_df(self, full_report=True) -> pd.DataFrame:
        if full_report == True:
            return pd.DataFrame(
                self.model_dump().items(),
                columns=["Field", "Value"]
            )
        else: # full report == False
            return pd.DataFrame(
                self.model_dump(
                        exclude={
                            "si_unit_polarity",
                            "valve_polarity",
                            "pe_port_entry",
                            "pilot_silencer_piping_type",
                            "lt_surge_volt_sup",
                            "coil_type",
                            "fitting_direction",
                            "port_measurement_type",
                            "number_of_stations",
                            "number_of_solenoids",
                            "parsed_valves",
                            "valves",
                            "sup_exh_blocks",
                            "valve_plate",
                            "si_unit_pn",
                            "mounting",
                            "porting_type"
                        }
                    ).items(),
                columns=["Field", "Value"]
            )
# ------------------------------------------------------------------------------------------    
    #  --- Overall Logic for Main Model ---
    def main_model_logic(self):
        
        # calcualted field (initially set to none) guards
        if self.number_of_solenoids is None:
            raise ValueError("total number of solenoids was not loaded properly")
        
        # ----- [Endplate Type/SI Unit Polarity] -----
        # --------------------------------------------
        
        # if no si unit is selected and endplate type is not Nil, raise error
        if self.si_unit == "0" and (self.endplate_type != "" or (self.io_unit_1 != "" or self.io_unit_2 != "" or self.io_unit_3 != "" or self.io_unit_4 != "" )):
            raise ValueError("No SI Unit was selected, endplate type must be nil")
        
        # ----- [Light Surge Voltage Suppressor & Coil Type] -----
        # --------------------------------------------------------
        
        # checking if no valves are to be selected via option "M", valve callout must not have valve/station options
        valid_D_S = r"^((0|[2-9]|1[0-6])D|(0|[2-9]|[12][0-9]|3[0-2])S)+$" # matches values for (2-16)D or (2-32)S
        if self.lt_surge_volt_sup_and_coil_type == 'M' and not re.fullmatch(valid_D_S, self.valve_callout):
            raise ValueError("If 'M' is selected for light surge voltage suppressor, valve callout must only be 'D' or 'S' combinations")
        
        # checking if the valve and si unit have the same polarity, or valve is non-polar to work with either si unit polarity
        if (self.valve_polarity != "Non-Polar") and (self.si_unit_polarity != self.valve_polarity) and (self.si_unit != '0'):
            raise ValueError("SI Unit and valve polarity must match unless a Non-Polar valve is selected")
        
        # ----- [Valve Callout] -----
        # ---------------------------
        
        # if repeating identical components are submitted (ex. "5AB2AB") this will be invalid (correct config is "7AB")
        if any(self.parsed_valves[i]["symbol"] == self.parsed_valves[i - 1]["symbol"] for i in range(1, len(self.parsed_valves))):
            raise ValueError('There are repeating components in valve callout section; please consolidate if not blocking disks')
        
        # No multiples of blocking disks allowed (ex. "3X", "2Y", "2Z")
        if any((self.parsed_valves[i]["symbol"] in ("X", "Y", "Z")) and (self.parsed_valves[i]["qty"] != 1) for i in range(1, (len(self.parsed_valves)))):
            raise ValueError("There are blocking disks in multiples listed in the valve callout section")
        
        # Blocking disks cannot be placed at the beginning or end of valve callout
        if (self.parsed_valves[0]["symbol"] in ("X", "Y", "Z")) or self.parsed_valves[-1]["symbol"] in ("X", "Y", "Z"):
            raise ValueError("A blocking disk cannot be selected as the first or last component in the valve callout")
        
        # if the valve callout section is too long (greater than 19 chars), raise error
        if len(self.valve_callout) > 19:
            raise ValueError("valve callout exceeds allowable maximum of 19 characters")
        
        # if the total number of solenoids for valves and or manifold stations (for manifold base only) configured exceeds limit of 32
        if self.number_of_solenoids > 32:
            raise ValueError("Current configuration of valves (and or manifold base) exceeds allowable 32 solenoids")
        
        # ----- [Sup/Exh Porting Direction and Cover Assembly] Tests -----
        # ----------------------------------------------------------------
        
        # if a supply blocking disk is selected, a PE porting option meant for both sides must be selected
        if (any(self.parsed_valves[i]["symbol"] in ("X", "Y", "Z") for i in range(1, (len(self.parsed_valves))))) and self.pe_port_entry not in ("B", "F", "J"):
            raise ValueError("If a blocking disk is selected in valve callout, P/E port entry must use an option that features both sides")
        
        # ----- [A/B Port Size] Tests -----
        # ---------------------------------
        
        # if a valve with a fitting_size property besides standard (1, 2, 3) and mixed fitting ab_port_size options are not selected, reject
        if (any(self.parsed_valves[i]["fitting_size"] != 0 for i in range(1, (len(self.parsed_valves))))) and self.ab_port_size not in ('71', '72', '73', '74', '75', '76'):
            raise ValueError('Valves with varied fitting sizes have been called out but AB port size does not specify mixed fittings')
        
        # ----- [Mounting and Nameplate] Tests -----
        # ------------------------------------------
        
        # Bottom ported manifold can only have direct mounting options selected
        if self.mounting_and_nameplate not in ('', 'AA', 'BA') and self.porting_type == '11':
            raise ValueError('Only direct mounting options are available for the type 11 bottom ported manifolds')
        
        return self

# ----------------------- Function to Run Model -----------------------
def run_main_model(part_number: str):
    print("\n --------------------------------------")

    try:
        print(f"\nParsing:{part_number}\n")
        parser = TokenMapParser(SY1_EX600_TOKEN_MAP)
        tokens = parser.parse(part_number)
        manifold_assy = SY1_EX600_MODEL(**tokens)
        print(manifold_assy.get_tokens_df())

        return manifold_assy, True

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
        
        return None, False

    # Parser is Throwing Error
    except ValueError as e:
        print(f"\nParse error: {e}")
        if "tokens" in locals():
            print("Partial Tokens Extracted")
            print(pd.DataFrame([tokens]).T)
        else:
            print("Parsing failed before any tokens could be generated.")
        
        return None, False

# --- To run from terminal
# python -c "import main_model; main_model.run_main_model('SY36-Q2-S-3AB2X-A11')"

# python -c "import main_model ; model, bool =  main_model.run_main_model('SY36-Q2-R-3AB2WH-A11') ; print(model.bom()) "

# --- To run from interactive terminal
# python -i main_model.py
# >>> model, bool = run_main_model('SY36-Q2-S-5AB-A11')

# >>> model, bool = run_main_model('SY36-Q2-S-5DE-A71')