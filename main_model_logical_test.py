from main_model import run_main_model

# ----- [Endplate Type/SI Unit Polarity] Tests -----

# Test 1) 
# if no SI unit is selected in section 2 (SI Unit), "nil" must be selected for endplate_type and all io_units
def test_no_si_unit_validation():
    # Case 1: valid pn
    _, is_valid_1 = run_main_model('SY36-0-RD-2AA-A11')
    assert is_valid_1 is True
    # Case 2 - invalid pn: endplate_type is selected
    _, is_valid_2 = run_main_model('SY36-02-RD-2AA-A11')
    assert is_valid_2 is False
    # Case 3 invalid pn: io_unit is selected
    _, is_valid_3 = run_main_model('SY36-02-RD-2AA-A11')
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