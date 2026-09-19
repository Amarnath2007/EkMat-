import re
import json
import logging
import httpx
from typing import Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger("ekmat.attributes")

# Known equipment specific types for discriminative matching
TYPE_PATTERNS = [
    # Valves - specific types first
    (r"\bGLOBE\b", "GLOBE VALVE"),
    (r"\bGATE\b", "GATE VALVE"),
    (r"\bBALL\b", "BALL VALVE"),
    (r"\bBUTTERFLY\b|\bBF VLV\b", "BUTTERFLY VALVE"),
    (r"\bCHECK\b|\bNRV\b|\bNON RETURN\b", "CHECK VALVE"),
    (r"\bPLUG\b", "PLUG VALVE"),
    (r"\bNEEDLE\b|\bNDL\b", "NEEDLE VALVE"),
    (r"\bSLUICE\b", "SLUICE VALVE"),
    (r"\bSAFETY RELIEF\b|\bSAFETY\b", "SAFETY RELIEF VALVE"),
    (r"\bCONTROL\b|\bCTRL\b", "CONTROL VALVE"),
    (r"\bDIAPHRAGM\b", "DIAPHRAGM VALVE"),
    # Bearings - specific models and types
    (r"\bNJ\s*205\b", "CYLINDRICAL ROLLER BEARING"),
    (r"\bNU\s*314\b", "CYLINDRICAL ROLLER BEARING"),
    (r"\bCYLINDRICAL ROLLER\b", "CYLINDRICAL ROLLER BEARING"),
    (r"\b6205\b|\bDGBB\b|\bDEEP GROOVE\b", "DEEP GROOVE BALL BEARING"),
    (r"\b22218\b|\bSPHERICAL ROLLER\b", "SPHERICAL ROLLER BEARING"),
    (r"\b32210\b|\bTAPER ROLLER\b|\bTAPERED ROLLER\b", "TAPERED ROLLER BEARING"),
    (r"\b7312\b|\bANGULAR CONTACT\b", "ANGULAR CONTACT BALL BEARING"),
    (r"\bUCP\s*208\b|\bPILLOW BLOCK\b", "PILLOW BLOCK BEARING"),
    (r"\b51106\b|\bTHRUST BALL\b", "THRUST BALL BEARING"),
    (r"\bHK\s*2016\b|\bNEEDLE\b", "NEEDLE ROLLER BEARING"),
    (r"\b1209\b|\bSELF ALIGN\b", "SELF ALIGNING BALL BEARING"),
    (r"\bC\s*2212\b|\bTOROIDAL\b|\bCARB\b", "TOROIDAL ROLLER BEARING"),
    (r"\bLMK\s*25\b|\bLINEAR\b", "LINEAR MOTION BUSHING"),
    # Pumps - specific pump architectures first
    (r"\bMULTISTAGE\b|\bBOOSTER\b|\bHIGH HEAD MULTISTAGE\b", "MULTISTAGE PUMP"),
    (r"\bBOILER FEED\b|\bBFP\b", "BOILER FEED PUMP"),
    (r"\bSPLIT CASE\b|\bFIRE WATER\b|\bHSC\b", "HORIZONTAL SPLIT CASE PUMP"),
    (r"\bPROGRESSIVE CAVITY\b|\bPC SCREW\b", "PROGRESSIVE CAVITY PUMP"),
    (r"\bVERTICAL TURBINE\b", "VERTICAL TURBINE PUMP"),
    (r"\bGEAR PUMP\b|\bROTARY GEAR\b", "GEAR PUMP"),
    (r"\bSUBMERSIBLE SUMP\b|\bDEWATERING\b", "SUBMERSIBLE DEWATERING PUMP"),
    (r"\bDOSING\b|\bMETERING\b|\bCHEMICAL INJECTION\b", "CHEMICAL DOSING PUMP"),
    (r"\bTRIPLEX\b|\bPLUNGER\b", "TRIPLEX PLUNGER PUMP"),
    (r"\bVACUUM\b|\bLRVP\b|\bLIQUID RING\b", "LIQUID RING VACUUM PUMP"),
    (r"\bBOREWELL\b|\bDEEP WELL\b", "BOREWELL SUBMERSIBLE PUMP"),
    (r"\bCANNED MOTOR\b|\bSEALLESS\b", "CANNED MOTOR PUMP"),
    (r"\bEND SUCTION\b|\bCENTRIFUGAL\b", "CENTRIFUGAL PUMP"),
    # Flanges - specific flange types
    (r"\bWNRF\b|\bWELD NECK\b|\bWELDING NECK\b", "WELD NECK FLANGE"),
    (r"\bSORF\b|\bSLIP ON\b", "SLIP ON FLANGE"),
    (r"\bBLRF\b|\bBLIND\b", "BLIND FLANGE"),
    (r"\bSWRF\b|\bSOCKET WELD\b", "SOCKET WELD FLANGE"),
    (r"\bLAP JOINT\b", "LAP JOINT FLANGE"),
    (r"\bTHREADED\b|\bSCREWED\b", "THREADED FLANGE"),
    (r"\bPLATE FLANGE\b|\bTABLE E\b", "PLATE FLANGE"),
    (r"\bSPECTACLE BLIND\b|\bFIGURE 8\b", "SPECTACLE BLIND"),
    (r"\bORIFICE\b", "ORIFICE FLANGE"),
    (r"\bRTJ\b", "RTJ FLANGE"),
    (r"\bSWIVEL\b", "SWIVEL RING FLANGE"),
    (r"\bREDUCING\b", "REDUCING FLANGE"),
]

MATERIAL_PATTERNS = [
    (r"\b(?:SS316|CF8M|STAINLESS STEEL 316)\b", "STAINLESS STEEL 316"),
    (r"\b(?:SS304|F304|STAINLESS STEEL 304)\b", "STAINLESS STEEL 304"),
    (r"\b(?:SS|STAINLESS STEEL)\b", "STAINLESS STEEL"),
    (r"\b(?:A105|WCB|CARBON STEEL|CS)\b", "CARBON STEEL"),
    (r"\b(?:MILD STEEL|MS|IS 2062)\b", "MILD STEEL"),
    (r"\b(?:CAST IRON|CI|FG260)\b", "CAST IRON"),
    (r"\b(?:DUCTILE IRON|DI|GGG40)\b", "DUCTILE IRON"),
    (r"\b(?:BRONZE|GUNMETAL)\b", "BRONZE"),
    (r"\b(?:ALLOY STEEL|F11|A182 F11)\b", "ALLOY STEEL F11"),
    (r"\bHASTELLOY\b", "HASTELLOY-C"),
]

PRESSURE_PATTERNS = [
    (r"\b(?:CLASS[- ]?150|150#|150\s*LBS?)\b", "CLASS 150"),
    (r"\b(?:CLASS[- ]?300|300#|300\s*LBS?)\b", "CLASS 300"),
    (r"\b(?:CLASS[- ]?600|600#|600\s*LBS?)\b", "CLASS 600"),
    (r"\b(?:CLASS[- ]?800|800#|800\s*LBS?)\b", "CLASS 800"),
    (r"\b(?:CLASS[- ]?900|900#|900\s*LBS?)\b", "CLASS 900"),
    (r"\b(?:3000\s*PSI|3000#)\b", "3000 PSI"),
    (r"\b(?:PN[- ]?16|16\s*BAR)\b", "PN16"),
    (r"\b(?:PN[- ]?10|10\s*BAR|10\s*KG/CM2)\b", "PN10"),
    (r"\b(?:PN[- ]?1\.0)\b", "PN 1.0"),
    (r"\b(?:150\s*BAR|150\s*KG/CM2)\b", "150 BAR"),
    (r"\b(?:6\s*BAR|6\s*KG/CM2)\b", "6 BAR"),
    (r"\b(?:8\s*BAR)\b", "8 BAR"),
]

SIZE_PATTERNS = [
    # Specific model numbers first (allowing space or hyphen)
    (r"\b(NJ[- ]?205)\b", "NJ 205 (25X52X15)"),
    (r"\b(NU[- ]?314)\b", "NU 314 (70X150X35)"),
    (r"\b(6205(?:\-2RS|\-ZZ)?)\b", "6205 (25X52X15)"),
    (r"\b(22218(?:\s*EK)?)\b", "22218 (90X160X40)"),
    (r"\b(32210)\b", "32210 (50X90X24.75)"),
    (r"\b(7312)\b", "7312 (60X130X31)"),
    (r"\b(UCP[- ]?208)\b", "UCP 208 (40MM)"),
    (r"\b(51106)\b", "51106 (30X47X11)"),
    (r"\b(HK[- ]?2016)\b", "HK 2016 (20X26X16)"),
    (r"\b(1209(?:\s*K)?)\b", "1209 (45X85X19)"),
    (r"\b(6310(?:\s*ZZ)?)\b", "6310 (50X110X27)"),
    (r"\b(C[- ]?2212)\b", "C 2212 (60X110X28)"),
    (r"\b(LMK[- ]?25)\b", "LMK 25 (25MM)"),
    # Pump ratings (support M3/HR and M3/H)
    (r"\b(50\s*M3/(?:HR|H).*?120M)\b", "50 M3/HR @ 120M HEAD"),
    (r"\b(50\s*M3/(?:HR|H).*?40M)\b", "50 M3/HR @ 40M HEAD"),
    (r"\b(10\s*LPM.*?10\s*BAR)\b", "10 LPM @ 10 BAR"),
    (r"\b(30\s*M3/(?:HR|H).*?15M)\b", "30 M3/HR @ 15M HEAD"),
    (r"\b(15\s*M3/(?:HR|H).*?6\s*BAR)\b", "15 M3/HR @ 6 BAR"),
    (r"\b(500\s*M3/(?:HR|H).*?25M)\b", "500 M3/HR @ 25M HEAD"),
    (r"\b(50\s*LPH.*?8\s*BAR)\b", "50 LPH @ 8 BAR"),
    (r"\b(80\s*M3/(?:HR|H).*?350M)\b", "80 M3/HR @ 350M HEAD"),
    (r"\b(2000\s*GPM.*?10\s*BAR)\b", "2000 GPM @ 10 BAR"),
    (r"\b(50\s*LPM.*?150\s*BAR)\b", "50 LPM @ 150 BAR"),
    (r"\b(100\s*M3/(?:HR|H).*?33\s*MBAR)\b", "100 M3/HR @ 33 MBAR"),
    (r"\b(25\s*M3/(?:HR|H).*?120M)\b", "25 M3/HR @ 120M HEAD"),
    (r"\b(15\s*M3/(?:HR|H).*?30M)\b", "15 M3/HR @ 30M HEAD"),
    # Generic sizes
    (r"\b(?:0\.5\s*(?:IN|INCH|\"|INCHES)|15\s*MM)\b", "15MM (0.5 INCH)"),
    (r"\b(?:1\s*(?:IN|INCH|\"|INCHES)|25\s*MM)\b", "25MM (1 INCH)"),
    (r"\b(?:1\.5\s*(?:IN|INCH|\"|INCHES)|40\s*MM)\b", "40MM (1.5 INCH)"),
    (r"\b(?:2\s*(?:IN|INCH|\"|INCHES)|50\s*MM)\b", "50MM (2 INCH)"),
    (r"\b(?:2\.5\s*(?:IN|INCH|\"|INCHES)|65\s*MM)\b", "65MM (2.5 INCH)"),
    (r"\b(?:3\s*(?:IN|INCH|\"|INCHES)|80\s*MM)\b", "80MM (3 INCH)"),
    (r"\b(?:4\s*(?:IN|INCH|\"|INCHES)|100\s*MM)\b", "100MM (4 INCH)"),
    (r"\b(?:6\s*(?:IN|INCH|\"|INCHES)|150\s*MM)\b", "150MM (6 INCH)"),
    (r"\b(?:8\s*(?:IN|INCH|\"|INCHES)|200\s*MM)\b", "200MM (8 INCH)"),
    (r"\b(?:10\s*(?:IN|INCH|\"|INCHES)|250\s*MM)\b", "250MM (10 INCH)"),
    (r"\b(?:12\s*(?:IN|INCH|\"|INCHES)|300\s*MM)\b", "300MM (12 INCH)"),
]

STANDARD_PATTERNS = [
    (r"\b(?:ASME\s*B16\.5|B16\.5)\b", "ASME B16.5"),
    (r"\b(?:ASME\s*B16\.10|B16\.10)\b", "ASME B16.10"),
    (r"\b(?:ASME\s*B16\.34|B16\.34)\b", "ASME B16.34"),
    (r"\b(?:ASME\s*B16\.48|B16\.48)\b", "ASME B16.48"),
    (r"\b(?:BS\s*10|TABLE\s*E)\b", "BS 10 TABLE E"),
    (r"\b(?:IS\s*14846)\b", "IS 14846"),
    (r"\b(?:ASTM\s*A216|A216\s*WCB)\b", "ASTM A216 WCB"),
    (r"\b(?:ASTM\s*A105|A105)\b", "ASTM A105"),
    (r"\b(?:ASTM\s*A182|A182)\b", "ASTM A182"),
]

CONNECTION_PATTERNS = [
    (r"\b(?:FLGD|FLANGED|RF|RAISED FACE)\b", "FLANGED RAISED FACE"),
    (r"\b(?:WAFER)\b", "WAFER"),
    (r"\b(?:SW|SOCKET WELD)\b", "SOCKET WELD"),
    (r"\b(?:NPT|THREADED|SCREWED)\b", "THREADED NPT"),
    (r"\b(?:WELD NECK|WNRF)\b", "WELD NECK"),
    (r"\b(?:SLIP ON|SORF)\b", "SLIP ON"),
    (r"\b(?:RTJ)\b", "RING TYPE JOINT (RTJ)"),
]

def extract_attributes_regex(text: str, spec: str = "") -> Dict[str, Any]:
    """
    High-fidelity rule-based attribute extractor.
    Extracts: material, size_mm, pressure_class, standard, type, connection.
    """
    combined = f"{text} {spec}".upper()
    attributes = {
        "type": None,
        "material": None,
        "size_mm": None,
        "pressure_class": None,
        "standard": None,
        "connection": None,
    }

    # Extract Type
    for pattern, val in TYPE_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            attributes["type"] = val
            break

    # Extract Material
    for pattern, val in MATERIAL_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            attributes["material"] = val
            break

    # Extract Pressure Class
    for pattern, val in PRESSURE_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            attributes["pressure_class"] = val
            break

    # Extract Size
    for pattern, val in SIZE_PATTERNS:
        match = re.search(pattern, combined, flags=re.IGNORECASE)
        if match:
            attributes["size_mm"] = val
            break

    # Extract Standard
    for pattern, val in STANDARD_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            attributes["standard"] = val
            break

    # Extract Connection
    for pattern, val in CONNECTION_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            attributes["connection"] = val
            break

    return attributes


async def extract_attributes(text: str, spec: str = "", category: str = "") -> Dict[str, Any]:
    """
    Primary extraction routine:
    1. Uses the deterministic regex/rule extractor as baseline.
    2. Attempts Ollama / Llama 3 JSON query with a short timeout.
    3. If Ollama is available, enhances the attributes; otherwise seamlessly returns the rule output.
    """
    rule_attrs = extract_attributes_regex(text, spec)

    # Attempt LLM extraction if enabled/available
    try:
        prompt = (
            f"Extract technical attributes from this CPSE material record as JSON.\n"
            f"Category: {category}\nDescription: {text}\nSpecification: {spec}\n"
            f"Respond with JSON format having keys: material, size_mm, pressure_class, standard, type, connection."
        )
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                llm_output = json.loads(data.get("response", "{}"))
                # Merge: prefer non-null LLM attributes if valid
                for k in rule_attrs.keys():
                    if not rule_attrs[k] and llm_output.get(k):
                        rule_attrs[k] = str(llm_output[k]).upper()
    except Exception as e:
        # Fallback is active and expected when Ollama is not running in local environment
        logger.debug(f"Ollama call skipped or timed out: {e}. Using regex extractor.")

    return rule_attrs
