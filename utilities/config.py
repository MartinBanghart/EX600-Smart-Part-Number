import os
import yaml 

BASE_DIR = os.path.dirname(__file__)
YAML_PATH = os.path.join(BASE_DIR, "field_values.yaml")

with open(YAML_PATH, "r") as f:
    YAML_DATA = yaml.safe_load(f)
