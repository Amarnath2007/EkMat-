import re
from backend.app.services.code_generation import generate_suggested_common_code

def test_code_generation_format():
    attrs = {
        "material": "CARBON STEEL",
        "size_mm": "150MM (6 INCH)",
        "type": "GATE VALVE"
    }
    code = generate_suggested_common_code("VALVE", attrs, sequence_num=1)
    
    # Assert prefix
    assert code.startswith("EKMAT-VALVE-")
    # Assert sequence ends with 001
    assert code.endswith("-001")
    # Assert regex structure: EKMAT-{CATEGORY}-{MATERIAL}-{SPEC}-{SEQUENCE}
    pattern = r"^EKMAT-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-\d{3}$"
    assert re.match(pattern, code), f"Code {code} did not match pattern {pattern}"

def test_code_generation_uniqueness():
    codes = set()
    for seq in range(1, 20):
        c = generate_suggested_common_code("BEARING", {"material": "STEEL", "size_mm": "6205"}, sequence_num=seq)
        assert c not in codes
        codes.add(c)
    assert len(codes) == 19
