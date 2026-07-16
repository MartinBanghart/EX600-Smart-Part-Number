# python -m pytest main_model_logical_test.py
# python -m pytest -s -k test_sup_exh_part_numbers 
# pytest -k "function name"

from main_model import run_main_model
from utilities.general_functions import load_test_part_numbers_from_excel

from pprint import pformat

# loading part number data
from pathlib import Path
FILE = Path(__file__).parent / "utilities/test_part_numbers.xlsx"
df_sup_exh = load_test_part_numbers_from_excel(FILE)

# ----- [Endplate Type/SI Unit Polarity] Tests -----

# Test 1) 
# if no SI unit is selected in section 2 (SI Unit), "nil" must be selected for endplate_type and all io_units
def test_no_si_unit_validation():
    # Case 1: valid pn
    _, is_valid_1, _ = run_main_model('SY36-0-R-2AA-A11')
    assert is_valid_1 is True
    # Case 2 - invalid pn: endplate_type is selected
    _, is_false_2, _ = run_main_model('SY36-02-R-2AA-A11')
    assert is_false_2 is False
    # Case 3 invalid pn: io_unit is selected
    _, is_false_3, _ = run_main_model('SY36-02-R-2AA-A11')
    assert is_false_3 is False

# ----- [Light Surge Voltage Suppressor & Coil Type] Tests -----

# Test 1)
# if "M" is selected no valves should be selected only "0D" and "0S" options in valve callout allowed
def test_only_manifold_validation():
    # Case 1: valid pn: double wired
    _, is_valid_1, _ = run_main_model('SY36-0-M-12D-A11')
    assert is_valid_1 is True
    # Case 2 - valid pn: single wired
    _, is_valid_2, _ = run_main_model('SY36-0-M-20S-A11')
    assert is_valid_2 is True
    # Case 3 invalid pn: "M" is selected but valve type "AA" is selected
    _, is_false_3, _ = run_main_model('SY36-0-M-2AA-A11')
    assert is_false_3 is False

# Test 2)
# if polarity selected does not match polarity of SI unit endplate in section 3, raise an issue
def test_si_and_valve_polarity_validation():
    # Case 1: valid pn: NPN si unit (Q2), NPN valve (S)
    _, is_valid_1, _ = run_main_model('SY36-Q2-S-2AA-A11')
    assert is_valid_1 is True
    # Case 2: valid pn: PNP si unit (Q4), PNP valve (V)
    _, is_valid_2, _ = run_main_model('SY36-Q4-V-2AA-A11')
    assert is_valid_2 is True
    # Case 3: valid pn: PNP si unit (Q4), Non-Polar valve (R)
    _, is_valid_3, _ = run_main_model('SY36-Q4-R-2AA-A11')
    assert is_valid_3 is True
    # Case 4: valid pn: NPN si unit (Q2), Non-Polar valve (R)
    _, is_valid_4, _ = run_main_model('SY36-Q2-R-2AA-A11')
    assert is_valid_4 is True
    # Case 5: invalid pn: NPN si unit (Q2), PNP valve (V)
    _, is_false_5, _ = run_main_model('SY36-Q2-V-2AA-A11')
    assert is_false_5 is False
    
# ----- [Valve Callout] Tests -----

# 
def test_valve_callout_validation():
    # Case 1: checking if QTY of "1" is not allowed
    _, is_false_1, _ = run_main_model('SY36-Q2-S-1AA-A11')
    assert is_false_1 is False
    # Case 2: checking repeating identical components not allowed ("3AB2AB" should be "5AB") 
    _, is_false_2, _ = run_main_model('SY36-Q2-S-3AB2AB-A11')
    assert is_false_2 is False
    # Case 3: multiple blocking disks not allowed
    _, is_false_3, _ = run_main_model('SY36-Q2-S-3AB2X-A11')
    assert is_false_3 is False
    # Case 4: valve callout section length is over 19 characters (ex. ABAA2AB2AA3AB3AA4AB4AA ; 22 characters, 20 valves)
    _, is_false_4, _ = run_main_model('SY36-Q2-S-ABAA2AB2AA3AB3AA4AB4AA-A11')
    assert is_false_4 is False
    # Case 5: blocking disk at the start of valve callout --> not allowed
    _, is_false_5, _ = run_main_model('SY36-Q2-S-XABAA-A11')
    assert is_false_5 is False
    # Case 5: blocking disk at the end of valve callout --> not allowed
    _, is_false_6, _ = run_main_model('SY36-Q2-S-ABAAX-A11')
    assert is_false_6 is False
    
# ----- [Sup/Exh Porting Direction and Cover Assembly] Tests -----

#
def test_sup_exh_port_dir_and_cover_assy_validation():
    # Case 1: if a blocking disk is selected, a port entry type of "B" for both sides must be selected
    _, is_false_1, _ = run_main_model('SY36-0-R-2AAXAB-A11') # X blocking disc selected, "A" sup/exh selected which is u-side entry (should be "C" for b-side entry)
    assert is_false_1 is False
    
    
# ----- [A/B Port Size] Tests -----

#
def test_ab_port_size_validation():
    # Case 1: a valve with a fitting size valve of "-1" --> 'FC' but mixed fittings were not specified ("11")
    _, is_false_1, _ = run_main_model('SY36-0-R-2AA2FC-A11')
    assert is_false_1 is False
    

# ----- [Mounting and Nameplate] Tests -----

# 
def test_mounting_and_nameplate_validation():
    # Case 1: "B" sup/exh picked which is type 11 (bottom ported) and 'D0" mounting is selected which is din rail mounting, not direct mounting
    _, is_false_1, _ = run_main_model('SY36-0-R-2AA-B11-D0')
    assert is_false_1 is False
    
    
# --------------------------------------------
# ------------ PART NUMBER CHECKS ------------
# --------------------------------------------

def test_sup_exh_part_numbers():
    invalids = []
    
    for ind, item in enumerate(df_sup_exh['Overall PN']):
        item = str(item).strip()
        model, is_valid, _ = run_main_model(item)
        
        # verifying that the overall part number successfully ran in the main model
        if not is_valid or model is None:
            continue
        
        # grabbing generated supply exhaust pns from current intialized model
        if model.sup_exh_blocks:
            d_side_sup_exh_calc_pn = model.sup_exh_blocks[0]['D-Side Sup/Exh']
            u_side_sup_exh_calc_pn = model.sup_exh_blocks[1]['U-Side Sup/Exh']

        
        # grabbing verified supply exhaust part numbers from excel sheet
        u_side_sup_exh_pn = str(df_sup_exh['U Side Supply Exhaust PN'][ind]).strip()
        d_side_sup_exh_pn = str(df_sup_exh['D Side Supply Exhaust PN'][ind]).strip()
        
        # comparing part numbers and adding invalids into a list
        if (u_side_sup_exh_calc_pn != u_side_sup_exh_pn) or (d_side_sup_exh_calc_pn != d_side_sup_exh_pn):
            invalids.append({
                            "Overall": item,
                            "Calculated U Side": u_side_sup_exh_calc_pn,
                            "Expected U Side": u_side_sup_exh_pn,
                            "Calculated D Side": d_side_sup_exh_calc_pn,
                            "Expected D Side": d_side_sup_exh_pn,
                        })

    # checks if invalids is 0 (pass condition), if greater than 0 (fail condition) then outputs invalid part numbers
    assert not invalids, (
        f"\nFound {len(invalids)} invalid part numbers:\n"
        f"{pformat(invalids, sort_dicts=False)}"
    )

