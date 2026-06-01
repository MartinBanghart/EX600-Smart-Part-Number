# python -m pytest main_model_logical_test.py
# pytest -k "function name"

from main_model import run_main_model

# ----- [Endplate Type/SI Unit Polarity] Tests -----

# Test 1) 
# if no SI unit is selected in section 2 (SI Unit), "nil" must be selected for endplate_type and all io_units
def test_no_si_unit_validation():
    # Case 1: valid pn
    _, is_valid_1 = run_main_model('SY36-0-R-2AA-A11')
    assert is_valid_1 is True
    # Case 2 - invalid pn: endplate_type is selected
    _, is_valid_2 = run_main_model('SY36-02-R-2AA-A11')
    assert is_valid_2 is False
    # Case 3 invalid pn: io_unit is selected
    _, is_valid_3 = run_main_model('SY36-02-R-2AA-A11')
    assert is_valid_3 is False

# ----- [Light Surge Voltage Suppressor & Coil Type] Tests -----

# Test 1)
# if "M" is selected no valves should be selected only "0D" and "0S" options in valve callout allowed
def test_only_manifold_validation():
    # Case 1: valid pn: double wired
    _, is_valid_1 = run_main_model('SY36-Q2-M-12D-A11')
    assert is_valid_1 is True
    # Case 2 - valid pn: single wired
    _, is_valid_2 = run_main_model('SY36-Q2-M-20S-A11')
    assert is_valid_2 is True
    # Case 3 invalid pn: "M" is selected but valve type "AA" is selected
    _, is_valid_3 = run_main_model('SY36-Q2-M-2AA-A11')
    assert is_valid_3 is False

# Test 2)
# if polarity selected does not match polarity of SI unit endplate in section 3, raise an issue
def test_si_and_valve_polarity_validation():
    # Case 1: valid pn: NPN si unit (Q2), NPN valve (S)
    _, is_valid_1 = run_main_model('SY36-Q2-S-2AA-A11')
    assert is_valid_1 is True
    # Case 2: valid pn: PNP si unit (Q4), PNP valve (V)
    _, is_valid_1 = run_main_model('SY36-Q4-V-2AA-A11')
    assert is_valid_1 is True
    # Case 3: valid pn: PNP si unit (Q4), Non-Polar valve (R)
    _, is_valid_1 = run_main_model('SY36-Q4-R-2AA-A11')
    assert is_valid_1 is True
    # Case 4: valid pn: NPN si unit (Q2), Non-Polar valve (R)
    _, is_valid_1 = run_main_model('SY36-Q2-R-2AA-A11')
    assert is_valid_1 is True
    # Case 5: invalid pn: NPN si unit (Q2), PNP valve (V)
    _, is_valid_1 = run_main_model('SY36-Q2-V-2AA-A11')
    assert is_valid_1 is False