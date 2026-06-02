import os
import yaml 

BASE_DIR = os.path.dirname(__file__)

# Overall data for the main model callouts
YAML_PATH = os.path.join(BASE_DIR, "field_values.yaml")
with open(YAML_PATH, "r") as f:
    YAML_DATA = yaml.safe_load(f)
    
# --- HTO Table Data ---
# U Side Supply Exhaust Block Assembly
sup_exh_tables_PATH = os.path.join(BASE_DIR, "sup_exh_block_hto_tables.yaml")
with open(sup_exh_tables_PATH, "r") as f:
    sup_exh_tables = yaml.safe_load(f)
    
# Cover and Port Block Assembly
port_block_PATH = os.path.join(BASE_DIR, "cover_and_port_block_assy_hto_tables.yaml")
with open(port_block_PATH, "r") as f:
    port_block_tables = yaml.safe_load(f)

# A/B Port Mixed Fitting Size Guide
ab_mixed_fitting_PATH = os.path.join(BASE_DIR, "ab_port_mixed_fitting_size_guide.yaml")
with open(ab_mixed_fitting_PATH, "r") as f:
    ab_mixed_fitting_tables = yaml.safe_load(f)