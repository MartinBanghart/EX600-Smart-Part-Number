# Dependencies
import re
import pandas as pd
from pydantic import BaseModel

# Loading data
from utilities.config import YAML_DATA

# ---------------------------------------------------------------------------------
# # --- Parser for Main Model --> Tokenizes user input ---
class TokenMapParser:
    def __init__(self, token_map):
        self.token_map = token_map
        # tokens allowed to match empty string
        self.allow_empty = {"mounting_and_nameplate", "endplate_type", 
                            "io_unit_1", "io_unit_2", "io_unit_3", "io_unit_4", "manual_override"}

    def parse(self, raw_string):
        s = raw_string.strip().upper()
        result = {}
        i = 0

        for token in self.token_map:
            name = token["name"]
            pattern = token["pattern"]
            length = token.get("length")

            # -------------------------------
            # FIXED LENGTH TOKENS
            # -------------------------------
            if length is not None:
                segment = s[i:i+length]
                if not re.fullmatch(pattern, segment):
                    raise ValueError(
                        f"Token '{name}' at position {i} is invalid: '{segment}'"
                    )
                result[name] = segment
                i += length
                continue

            # -------------------------------
            # VARIABLE LENGTH TOKENS
            # -------------------------------
            match = re.match(pattern, s[i:])
            if match:
                segment = match.group()

                # allow empty match for specific tokens
                if segment == "":
                    if name in self.allow_empty:
                        result[name] = ""
                        continue
                    else:
                        raise ValueError(
                            f"Token '{name}' cannot match empty string at position {i}"
                        )

                # normal non-empty match
                result[name] = segment
                i += len(segment)
                continue

            # fallback for mounting (legacy behavior)
            if name in self.allow_empty:
                result[name] = ""
                continue

            raise ValueError(f"Token '{name}' could not be matched")

        if i != len(s):
            raise ValueError(f"Unexpected trailing characters after parsing: '{s[i:]}'")

        return result


# ---------------------------------------------------------------------------------
# --- Valve Callout Parser ---
# This runs as a field validator in the main model to ensure the valve callout section is accurate
# ---> it creates a dict of valve qty and symbols within model (info.data["_parsed_valves"] = parsed)

# ---- The below are required inputs for the function, these will need to be loaded in the file with main model
# all valid valve symbols --> currently has all options, including ones not used --> remember to clean to only used eventually
# ---> valid_valve_symbols = set(field_values["valve_symbols"].keys())

# compiles regex pattern for efficiency in loop
valve_qty_pattern = re.compile(r"(2[0-4]|1[0-9]|[2-9])")  # 2–24


def parse_valve_callout(callout: str, valid_symbols: set[str]):
    i = 0
    n = len(callout)
    result = []

    base_pos = 0

    while i < n:
        # try to read quantity
        qty_match = valve_qty_pattern.match(callout, i)
        if qty_match:
            qty = int(qty_match.group())
            i = qty_match.end()
        else:
            qty = 1

        # interpreting symbol (prefer 2-char)
        symbol = None

        if i + 2 <= n:
            two = callout[i:i + 2]
            if two in valid_symbols:
                symbol = two
                i += 2

        if symbol is None and i + 1 <= n:
            one = callout[i:i + 1]
            if one in valid_symbols:
                symbol = one
                i += 1

        if symbol is None:
            raise ValueError(
                f"Invalid valve symbol at position {i}: '{callout[i:]}'"
            )

        # Position logic
        if symbol in {"X", "Y", "Z"}:
            pos = f"{base_pos}_{symbol}"
        else:
            base_pos += 1
            pos = base_pos

        valve_data = YAML_DATA["valve_symbols"][symbol]

        result.append(
            {
                "pos": pos,
                "qty": qty,
                "symbol": symbol,
                "fitting_size": valve_data["fitting_size"],
            }
        )

    return result

# ---------------------------------------------------------------------------------
def load_test_part_numbers_from_excel(filename):
    # read all sheets into a dictionary
    sheets_dict = pd.read_excel(filename, sheet_name=None)

    # extract specific dataframes using the exact sheet names
    df_sup_exh = sheets_dict['sup_exh']
    
    
    return df_sup_exh