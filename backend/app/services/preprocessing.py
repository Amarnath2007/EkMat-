import re
from typing import Tuple

ABBREVIATIONS = {
    r"\bMS\b": "MILD STEEL",
    r"\bCS\b": "CARBON STEEL",
    r"\bCI\b": "CAST IRON",
    r"\bSS\b": "STAINLESS STEEL",
    r"\bSS316\b": "STAINLESS STEEL 316",
    r"\bSS304\b": "STAINLESS STEEL 304",
    r"\bGI\b": "GALVANIZED IRON",
    r"\bDI\b": "DUCTILE IRON",
    r"\bNB\b": "NOMINAL BORE",
    r"\bPN\b": "PRESSURE NOMINAL",
    r"\bERW\b": "ELECTRIC RESISTANCE WELDED",
    r"\bSCH\b": "SCHEDULE",
    r"\bVLV\b": "VALVE",
    r"\bFLGD\b": "FLANGED",
    r"\bFLG\b": "FLANGE",
    r"\bCHK\b": "CHECK",
    r"\bNRV\b": "NON RETURN VALVE",
    r"\bBRG\b": "BEARING",
    r"\bDGBB\b": "DEEP GROOVE BALL BEARING",
    r"\bACBB\b": "ANGULAR CONTACT BALL BEARING",
    r"\bWCB\b": "CAST CARBON STEEL WCB",
    r"\bCF8M\b": "STAINLESS STEEL CF8M SS316",
    r"\bWNRF\b": "WELD NECK RAISED FACE",
    r"\bSORF\b": "SLIP ON RAISED FACE",
    r"\bBLRF\b": "BLIND RAISED FACE",
    r"\bSWRF\b": "SOCKET WELD RAISED FACE",
    r"\bRF\b": "RAISED FACE",
    r"\bSW\b": "SOCKET WELD",
    r"\bTDH\b": "TOTAL DYNAMIC HEAD",
    r"\bLPM\b": "LITRES PER MINUTE",
    r"\bLPH\b": "LITRES PER HOUR",
    r"\bM3/H\b": "M3/HR",
}

# Metric / Imperial size equivalences
SIZE_EQUIVALENCES = [
    (r'(\b0\.5\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b15\s*MM\b)', "15MM (0.5 INCH)"),
    (r'(\b1\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b25\s*MM\b)', "25MM (1 INCH)"),
    (r'(\b1\.5\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b40\s*MM\b)', "40MM (1.5 INCH)"),
    (r'(\b2\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b50\s*MM\b)', "50MM (2 INCH)"),
    (r'(\b2\.5\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b65\s*MM\b)', "65MM (2.5 INCH)"),
    (r'(\b3\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b80\s*MM\b)', "80MM (3 INCH)"),
    (r'(\b4\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b100\s*MM\b)', "100MM (4 INCH)"),
    (r'(\b6\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b150\s*MM\b)', "150MM (6 INCH)"),
    (r'(\b8\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b200\s*MM\b)', "200MM (8 INCH)"),
    (r'(\b10\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b250\s*MM\b)', "250MM (10 INCH)"),
    (r'(\b12\s*(?:IN|INCH|"|\'\'|INCHES)\b|\b300\s*MM\b)', "300MM (12 INCH)"),
]

def normalize_text(text: str) -> str:
    """
    Standardize material description:
    1. Uppercase & strip
    2. Expand standard CPSE abbreviations
    3. Harmonize dimension / size patterns
    4. Harmonize pressure ratings
    5. Clean punctuation & extra whitespace
    """
    if not text:
        return ""

    result = text.upper()

    # Expand abbreviations
    for pattern, replacement in ABBREVIATIONS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Standardize pressure ratings like 150#, 150 LBS, CLASS 150, CLASS-150 -> CLASS 150
    result = re.sub(r'(\bCLASS[- ]?(\d+)\b|\b(\d+)\s*(?:#|LBS|LB)\b)', r'CLASS \2\3', result)
    result = re.sub(r'\bPN[- ]?(\d+)\b', r'PN\1', result)

    # Harmonize common size mentions
    for pattern, std_size in SIZE_EQUIVALENCES:
        result = re.sub(pattern, std_size, result, flags=re.IGNORECASE)

    # Remove extraneous symbols while preserving key spec delimiters
    result = re.sub(r'[,\/\\\(\)\[\]\-]+', ' ', result)
    result = re.sub(r'\s+', ' ', result).strip()

    return result
