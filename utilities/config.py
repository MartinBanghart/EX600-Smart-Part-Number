import os
import yaml 

BASE_DIR = os.path.dirname(__file__)

# Overall data for the main model callouts
YAML_PATH = os.path.join(BASE_DIR, "field_values.yaml")
with open(YAML_PATH, "r") as f:
    YAML_DATA = yaml.safe_load(f)
    
# --- HTO Table Data ---
# U Side Supply Exhaust Block Assembly
u_side_sup_exh_tables_PATH = os.path.join(BASE_DIR, "u_side_sup_exh_block_hto_tables.yaml")
with open(u_side_sup_exh_tables_PATH, "r") as f:
    u_side_sup_exh_tables = yaml.safe_load(f)