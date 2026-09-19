#!/usr/bin/env python3
"""
EkMat Synthetic Dataset Generator (SIH26099)
Generates ~200 realistic CPSE material master records across 5 CPSEs:
  - BHEL (Bharat Heavy Electricals Limited) - SAP ECC
  - ONGC (Oil and Natural Gas Corporation) - SAP S/4HANA
  - GAIL (Gas Authority of India Limited) - SAP ECC
  - NTPC (National Thermal Power Corporation) - SAP S/4HANA
  - SAIL (Steel Authority of India Limited) - SAP ECC

Categories: VALVE, BEARING, PUMP, FLANGE
Includes:
  - Equivalent clusters (abbreviation variants, unit variants, re-ordered descriptions)
  - Deliberate near-miss non-matches (e.g. Gate Valve vs Globe Valve, Ball vs Roller Bearing)
  - Ground truth cluster IDs for defensible precision/recall testing.
"""

import os
import csv

# Ground truth clusters definition
# Each cluster contains a list of CPSE records that genuinely match the same physical equipment.
# Near-misses have distinct ground_truth_cluster IDs so they must NOT cluster together.

CLUSTERS_DATA = [
    # =========================================================================
    # CATEGORY: VALVE (~10 clusters + deliberate near-misses)
    # =========================================================================
    {
        "category": "VALVE",
        "name": "6in CS Gate Valve ASME 150",
        "ground_truth_id": "VLV-CL-001",
        "records": [
            ("BHEL", "BHEL-94100281", "VLV GATE 6IN 150# CS FLGD ASTM A216 WCB", "SIZE: 6 INCH, RATING: 150 LB, BODY: WCB, END: FLANGED", "NOS"),
            ("ONGC", "ONGC-M-74892", "6\" (150 MM) CARBON STEEL GATE VALVE CLASS-150 FLANGED ENDS WCB BODY", "6 INCH NB, 150 LBS RF, A216 WCB OS&Y", "EA"),
            ("GAIL", "GAIL-MAT-30419", "VALVE, GATE, FLANGED, 150 LBS, 6 INCH NOMINAL BORE, CS BODY", "ASME B16.10, ASME B16.5 150#, BODY CS", "NOS"),
            ("NTPC", "NTPC-GEN-55201", "GATE VALVE 150MM NB 150 CLASS WCB CS RF FLANGED OS&Y", "150 MM NB, ASME CLASS 150, WCB BODY FLANGED", "NOS"),
            ("SAIL", "SAIL-BSP-80921", "CARBON STEEL GATE VALVE 6\" ASME B16.10/B16.5 CLASS 150 FLGD", "6 INCH, CS CAST STEEL, CLASS 150 FLANGED", "SET"),
        ]
    },
    # DELIBERATE NEAR-MISS 1: Globe Valve with same size & rating. MUST NOT MERGE with VLV-CL-001!
    {
        "category": "VALVE",
        "name": "6in CS Globe Valve ASME 150 (NEAR MISS to Gate Valve)",
        "ground_truth_id": "VLV-NM-001",
        "records": [
            ("BHEL", "BHEL-94100289", "VLV GLOBE 6IN 150# CS FLGD ASTM A216 WCB", "SIZE: 6 INCH, RATING: 150 LB, BODY: WCB, END: FLANGED, TYPE: GLOBE", "NOS"),
            ("ONGC", "ONGC-M-74899", "6\" (150 MM) CS GLOBE VALVE CLASS-150 FLANGED WCB", "6 INCH NB, 150 LBS RF, GLOBE PATTERN, A216 WCB", "EA"),
            ("GAIL", "GAIL-MAT-30425", "VALVE, GLOBE, FLANGED, 150 LBS, 6 INCH NB, CS", "ASME B16.10 GLOBE VALVE 150# RF", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "2in SS316 Ball Valve Class 300",
        "ground_truth_id": "VLV-CL-002",
        "records": [
            ("BHEL", "BHEL-94100305", "BALL VLV 2IN 300# SS316 2PC FLGD", "SIZE 2 INCH, 300 LBS, SS316 BODY, FULL BORE", "NOS"),
            ("ONGC", "ONGC-M-75012", "2\" SS BALL VALVE CL-300 FLANGED ENDS CF8M", "50 MM NB, ASME CL 300, SS 316 / CF8M", "EA"),
            ("GAIL", "GAIL-MAT-30520", "VALVE, BALL, 2\", CLASS 300, STAINLESS STEEL 316, FLANGED", "2 INCH, 300#, SS 316, ASME B16.5", "NOS"),
            ("NTPC", "NTPC-GEN-55310", "BALL VALVE 50MM NB 300 CLASS CF8M STAINLESS STEEL RF", "50MM, CLASS 300, FULL BORE BALL VALVE", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "4in Cast Iron Butterfly Valve PN16 Wafer",
        "ground_truth_id": "VLV-CL-003",
        "records": [
            ("BHEL", "BHEL-94100412", "BF VLV 4IN PN16 CI WAFER EPDM LINED", "SIZE 4\", PN 16, BODY CAST IRON, WAFER TYPE", "NOS"),
            ("SAIL", "SAIL-BSP-81204", "BUTTERFLY VALVE 100MM PN16 WAFER CI DISC SS", "100 MM NB, PRESSURE PN16, CAST IRON BODY", "NOS"),
            ("NTPC", "NTPC-GEN-55440", "4\" CI WAFER BUTTERFLY VALVE PN 16 WITH LEVER", "4 INCH (100MM), RATING PN16, BODY CI FG260", "EA"),
            ("GAIL", "GAIL-MAT-30611", "VALVE, BUTTERFLY, 4 INCH, PN16, CAST IRON, WAFER", "100MM NOMINAL, PN 16 BAR, EPDM SEAT", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "1in Forged Steel Check Valve Class 800 Socket Weld",
        "ground_truth_id": "VLV-CL-004",
        "records": [
            ("BHEL", "BHEL-94100520", "NRV CHK VLV 1IN 800# FS SW A105", "1 INCH, CLASS 800, FORGED CARBON STEEL, SW ENDS", "NOS"),
            ("ONGC", "ONGC-M-75218", "1\" FORGED STEEL LIFT CHECK VALVE 800 LBS SW A105", "25 MM NB, 800#, ASTM A105 PISTON CHECK", "EA"),
            ("GAIL", "GAIL-MAT-30715", "VALVE, CHECK, 1\", CLASS 800, FORGED STEEL, SOCKET WELD", "BS 5352, CL 800, SW ENDS", "NOS"),
            ("SAIL", "SAIL-BSP-81340", "CHECK VALVE FORGED CARBON STEEL 25MM CLASS 800 SW", "25MM NB, A105, 800 LBS", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "3in Mild Steel Plug Valve Class 150",
        "ground_truth_id": "VLV-CL-005",
        "records": [
            ("BHEL", "BHEL-94100615", "PLUG VLV 3IN 150# MS FLGD PTFE SLEEVED", "3 INCH, 150#, MILD STEEL BODY, FLANGED", "NOS"),
            ("GAIL", "GAIL-MAT-30810", "VALVE, PLUG, 3 INCH, 150 LBS, MILD STEEL, FLANGED RF", "80MM NB, CLASS 150, MS BODY", "NOS"),
            ("NTPC", "NTPC-GEN-55519", "PLUG VALVE 80MM NB 150 CLASS MS RF FLANGED", "80 MM (3\"), CLASS 150, PTFE SLEEVE", "EA"),
            ("ONGC", "ONGC-M-75340", "3\" MS PLUG VALVE CL 150 FLANGED ENDS", "3 INCH, 150 LBS, SLEEVED PLUG VALVE", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "8in Cast Steel Swing Check Valve Class 150",
        "ground_truth_id": "VLV-CL-006",
        "records": [
            ("BHEL", "BHEL-94100722", "SWING CHK VLV 8IN 150# CS FLGD WCB", "SIZE 8\", RATING 150 LB, WCB BODY, FLANGED", "NOS"),
            ("ONGC", "ONGC-M-75460", "8\" (200 MM) CS NON RETURN VALVE CL-150 FLANGED WCB", "200 MM NB, ASME 150, CAST STEEL SWING CHECK", "EA"),
            ("SAIL", "SAIL-BSP-81490", "NON-RETURN VALVE 8\" CLASS 150 WCB CAST STEEL FLGD", "8 INCH, CLASS 150, BS 1868 / ASME B16.34", "NOS"),
            ("NTPC", "NTPC-GEN-55620", "SWING CHECK VALVE 200MM NB 150 CLASS CS RF", "200MM, 150#, ASTM A216 WCB", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "0.5in SS Needle Valve 3000 PSI NPT",
        "ground_truth_id": "VLV-CL-007",
        "records": [
            ("BHEL", "BHEL-94100801", "NDL VLV 1/2IN 3000 PSI SS316 NPT F", "1/2 INCH, 3000 PSI, SS 316, FEMALE NPT", "NOS"),
            ("ONGC", "ONGC-M-75510", "1/2\" NEEDLE VALVE 3000# SS316 NPT FEMALE ENDS", "15 MM, 3000 PSIG, STAINLESS STEEL 316", "EA"),
            ("GAIL", "GAIL-MAT-30905", "VALVE, NEEDLE, 1/2\", 3000 PSI, SS316, THREADED NPT", "1/2 INCH NPT, 3000 LBS, BARSTOCK SS316", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "12in Cast Steel Sluice Gate Valve PN 1.0",
        "ground_truth_id": "VLV-CL-008",
        "records": [
            ("BHEL", "BHEL-94100910", "SLUICE VLV 12IN PN 1.0 CS FLGD IS 14846", "300MM NB, PN 1.0 MPA, CAST STEEL, FLANGED", "NOS"),
            ("NTPC", "NTPC-GEN-55730", "SLUICE VALVE 300MM NB PN 1.0 MPA CS BODY FLGD", "12 INCH (300 MM), PN 10 / 1.0 MPA, FLANGED", "NOS"),
            ("SAIL", "SAIL-BSP-81610", "12\" CS SLUICE VALVE PN10 FLANGED AS PER IS 14846", "300 MM, RATING PN 1.0, CS BODY", "SET"),
        ]
    },
    {
        "category": "VALVE",
        "name": "2.5in Bronze Safety Relief Valve 10 Bar",
        "ground_truth_id": "VLV-CL-009",
        "records": [
            ("BHEL", "BHEL-94101015", "SAFETY RELIEF VLV 2.5IN 10 BAR BRONZE FLGD", "65MM NB, SET PRESSURE 10 BAR, BRONZE BODY", "NOS"),
            ("ONGC", "ONGC-M-75625", "2-1/2\" BRONZE SAFETY VALVE SET 10 KG/CM2 FLANGED", "65 MM, 10 KG/SQ CM, BRONZE / GUNMETAL", "EA"),
            ("GAIL", "GAIL-MAT-31015", "VALVE, SAFETY RELIEF, 2.5 INCH, 10 BAR, BRONZE", "2.5\", 10 BAR G, BRONZE CONSTRUCTION", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "10in Ductile Iron Control Valve PN16",
        "ground_truth_id": "VLV-CL-010",
        "records": [
            ("BHEL", "BHEL-94101130", "CTRL VLV 10IN PN16 DI PNEUMATIC ACTUATED FLGD", "250MM, PN16, DUCTILE IRON, WITH ACTUATOR", "NOS"),
            ("NTPC", "NTPC-GEN-55840", "CONTROL VALVE 250MM NB PN16 DUCTILE IRON FLANGED", "10 INCH, PN 16, DI BODY GGG40, 4-20MA", "NOS"),
            ("SAIL", "SAIL-BSP-81725", "10\" DUCTILE IRON CONTROL VALVE PN16 WITH POSITIONER", "250 MM NB, PRESSURE CLASS PN16, DI", "SET"),
            ("ONGC", "ONGC-M-75780", "10\" DI CONTROL VALVE CLASS PN-16 FLANGED ENDS", "250MM, PN 16, DUCTILE IRON", "EA"),
        ]
    },
    {
        "category": "VALVE",
        "name": "3in CI Diaphragm Valve Flanged PN10",
        "ground_truth_id": "VLV-CL-011",
        "records": [
            ("BHEL", "BHEL-94101240", "DIAPHRAGM VLV 3IN PN10 CI WEIR TYPE FLGD", "80MM NB, PN10, CAST IRON WEIR TYPE NEOPRENE LINED", "NOS"),
            ("GAIL", "GAIL-MAT-31120", "VALVE, DIAPHRAGM, 3\", PN10, CAST IRON, WEIR TYPE", "3 INCH (80MM), PN 10, RUBBER DIAPHRAGM", "NOS"),
            ("SAIL", "SAIL-BSP-81830", "3\" CI DIAPHRAGM VALVE FLANGED PN10 NEOPRENE", "80MM NB, PN10 RATING, CI BODY", "NOS"),
            ("NTPC", "NTPC-GEN-55950", "DIAPHRAGM VALVE 80MM NB PN10 CAST IRON FLANGED", "3 INCH, WEIR PATTERN, PN10 FLANGED", "NOS"),
        ]
    },
    {
        "category": "VALVE",
        "name": "4in Cryogenic Gate Valve Class 300 SS316",
        "ground_truth_id": "VLV-CL-012",
        "records": [
            ("BHEL", "BHEL-94101350", "CRYOGENIC GATE VLV 4IN 300# SS316 EXT BONNET", "100MM NB, CLASS 300, EXTENDED BONNET CRYO GATE", "NOS"),
            ("ONGC", "ONGC-M-75890", "4\" CRYOGENIC GATE VALVE CLASS-300 FLANGED SS316", "4 INCH (100MM), 300 LBS, SS316 EXTENDED STEM", "EA"),
            ("GAIL", "GAIL-MAT-31230", "VALVE, GATE, CRYOGENIC, 4\", 300#, SS316, FLANGED", "100MM NB, 300#, EXTENDED BONNET LNG SERVICE", "NOS"),
        ]
    },

    # =========================================================================
    # CATEGORY: BEARING (~10 clusters + deliberate near-misses)
    # =========================================================================
    {
        "category": "BEARING",
        "name": "Deep Groove Ball Bearing 6205-2RS",
        "ground_truth_id": "BRG-CL-001",
        "records": [
            ("BHEL", "BHEL-88200101", "BRG BALL DGBB 6205-2RS 25X52X15", "BORE: 25MM, OD: 52MM, W: 15MM, RUBBER SEAL BOTH SIDES", "NOS"),
            ("ONGC", "ONGC-B-41005", "BEARING 6205 2RS DEEP GROOVE BALL 25 MM BORE", "25X52X15 MM, DOUBLE RUBBER CONTACT SEAL", "EA"),
            ("GAIL", "GAIL-BRG-12001", "BALL BEARING, DEEP GROOVE, 6205-2RS, 25X52X15 MM", "6205 2RS DGBB C3 CLEARANCE RUBBER SEALED", "NOS"),
            ("NTPC", "NTPC-BRG-61010", "DEEP GROOVE BALL BEARING 6205 2RS1 SKF/FAG EQUIV", "25MM X 52MM X 15MM, DUAL SEAL 2RS", "NOS"),
            ("SAIL", "SAIL-BRG-70115", "RADIAL BALL BEARING 6205-2RSR (25X52X15)", "6205-2RS, ID 25, OD 52, B 15 MM", "NOS"),
        ]
    },
    # DELIBERATE NEAR-MISS 2: Cylindrical Roller Bearing with identical boundary dimensions (25x52x15). MUST NOT MERGE with 6205-2RS!
    {
        "category": "BEARING",
        "name": "Cylindrical Roller Bearing NJ 205 (NEAR MISS to 6205)",
        "ground_truth_id": "BRG-NM-001",
        "records": [
            ("BHEL", "BHEL-88200109", "BRG ROLLER CYLINDRICAL NJ 205 ECP 25X52X15", "BORE: 25MM, OD: 52MM, W: 15MM, CYLINDRICAL ROLLER", "NOS"),
            ("ONGC", "ONGC-B-41012", "BEARING NJ-205 CYLINDRICAL ROLLER 25X52X15 MM", "NJ 205, 25MM BORE, ROLLER BEARING", "EA"),
            ("SAIL", "SAIL-BRG-70125", "CYLINDRICAL ROLLER BEARING NJ205 (25X52X15 MM)", "NJ 205 E, ROLLER BEARING 25 MM SHAFT", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Spherical Roller Bearing 22218 EK",
        "ground_truth_id": "BRG-CL-002",
        "records": [
            ("BHEL", "BHEL-88200210", "BRG ROLLER SPHERICAL 22218 EK TAPER BORE", "90X160X40 MM, TAPERED BORE 1:12, SPHERICAL ROLLER", "NOS"),
            ("SAIL", "SAIL-BRG-70230", "SPHERICAL ROLLER BEARING 22218-E1-K (90X160X40)", "ID 90MM, OD 160MM, WIDTH 40MM, TAPERED BORE", "NOS"),
            ("NTPC", "NTPC-BRG-61120", "22218 EK SPHERICAL ROLLER BEARING WITH ADAPTER SLEEVE", "90X160X40, TAPER BORE 22218K", "EA"),
            ("ONGC", "ONGC-B-41130", "BEARING 22218 EK / C3 SPHERICAL ROLLER 90 MM BORE", "90 MM ID, 160 MM OD, 40 MM WIDTH", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Tapered Roller Bearing 32210",
        "ground_truth_id": "BRG-CL-003",
        "records": [
            ("BHEL", "BHEL-88200315", "BRG TAPER ROLLER 32210 50X90X24.75", "50X90X24.75 MM, TAPER ROLLER BEARING METRIC", "NOS"),
            ("GAIL", "GAIL-BRG-12110", "TAPERED ROLLER BEARING 32210, 50X90X24.75 MM", "32210 CONE AND CUP COMPLETE SET", "NOS"),
            ("SAIL", "SAIL-BRG-70340", "BEARING 32210 TAPER ROLLER (50X90X25)", "50 MM BORE, TAPER ROLLER, WIDTH 24.75 MM", "SET"),
            ("NTPC", "NTPC-BRG-61215", "32210 TAPER ROLLER BEARING 50MM BORE HEAVY DUTY", "BORE 50 MM, OD 90 MM, TAPERED ROLLER", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Angular Contact Ball Bearing 7312 BECBP",
        "ground_truth_id": "BRG-CL-004",
        "records": [
            ("BHEL", "BHEL-88200420", "BRG ANGULAR CONTACT 7312 BECBP 60X130X31", "60X130X31 MM, 40 DEG CONTACT ANGLE, BRASS CAGE", "NOS"),
            ("ONGC", "ONGC-B-41220", "BEARING 7312 ACBB SINGLE ROW 60 MM BORE", "60X130X31 MM, ANGULAR CONTACT BALL BEARING", "EA"),
            ("GAIL", "GAIL-BRG-12215", "BALL BEARING, ANGULAR CONTACT, 7312, 60X130X31 MM", "7312 B, 40 DEGREE ANGLE, 60 MM SHAFT", "NOS"),
            ("NTPC", "NTPC-BRG-61320", "7312 BECBM ANGULAR CONTACT BEARING 60MM", "60X130X31, BRASS CAGE ANGULAR BALL BEARING", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Pillow Block Bearing Unit UCP 208",
        "ground_truth_id": "BRG-CL-005",
        "records": [
            ("BHEL", "BHEL-88200505", "PLW BLK BRG UNIT UCP 208 40MM CAST IRON HOUSING", "40MM SHAFT DIA, 2-BOLT PILLOW BLOCK, CI HOUSING", "NOS"),
            ("SAIL", "SAIL-BRG-70450", "PILLOW BLOCK UNIT UCP 208 (40 MM BORE)", "UCP-208 HOUSING WITH INSERT BEARING UC208", "SET"),
            ("NTPC", "NTPC-BRG-61430", "UCP208 PEDESTAL BEARING UNIT 40MM SHAFT", "PILLOW BLOCK HOUSING CAST IRON 40MM", "NOS"),
            ("GAIL", "GAIL-BRG-12320", "BEARING UNIT, PILLOW BLOCK, UCP 208, 40 MM", "40MM BORE INSERT BEARING IN CAST HOUSING", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Thrust Ball Bearing 51106",
        "ground_truth_id": "BRG-CL-006",
        "records": [
            ("BHEL", "BHEL-88200612", "BRG THRUST BALL 51106 30X47X11", "30X47X11 MM, SINGLE DIRECTION THRUST BALL", "NOS"),
            ("ONGC", "ONGC-B-41315", "BEARING 51106 THRUST BALL 30 MM BORE", "30X47X11 MM, AXIAL THRUST BALL BEARING", "EA"),
            ("SAIL", "SAIL-BRG-70520", "THRUST BALL BEARING 51106 (30X47X11 MM)", "ID 30, OD 47, THICKNESS 11 MM", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Needle Roller Bearing HK 2016",
        "ground_truth_id": "BRG-CL-007",
        "records": [
            ("BHEL", "BHEL-88200718", "BRG NEEDLE DRAWN CUP HK 2016 20X26X16", "20X26X16 MM, DRAWN CUP NEEDLE ROLLER", "NOS"),
            ("GAIL", "GAIL-BRG-12410", "NEEDLE ROLLER BEARING HK 2016, 20X26X16 MM", "HK2016 DRAWN CUP CAGE ASSEMBLY", "NOS"),
            ("NTPC", "NTPC-BRG-61510", "HK 2016 NEEDLE BEARING 20MM ID 26MM OD 16MM W", "20X26X16, OPEN END NEEDLE ROLLER", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Self-Aligning Ball Bearing 1209 K",
        "ground_truth_id": "BRG-CL-008",
        "records": [
            ("BHEL", "BHEL-88200822", "BRG BALL SELF ALIGN 1209 K 45X85X19 TAPER", "45X85X19 MM, TAPER BORE SELF ALIGNING BALL", "NOS"),
            ("SAIL", "SAIL-BRG-70635", "SELF ALIGNING BALL BEARING 1209-K (45X85X19)", "BORE 45MM TAPERED, DOUBLE ROW BALL", "NOS"),
            ("ONGC", "ONGC-B-41410", "BEARING 1209 K SELF ALIGNING BALL 45 MM", "45X85X19 MM, TAPER BORE 1:12", "EA"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Deep Groove Ball Bearing 6310 ZZ",
        "ground_truth_id": "BRG-CL-009",
        "records": [
            ("BHEL", "BHEL-88200925", "BRG BALL DGBB 6310 ZZ 50X110X27 STEEL SHIELD", "50X110X27 MM, METAL SHIELD BOTH SIDES", "NOS"),
            ("ONGC", "ONGC-B-41520", "BEARING 6310-ZZ DEEP GROOVE BALL 50 MM BORE", "50X110X27 MM, DUAL METAL SHIELD", "EA"),
            ("NTPC", "NTPC-BRG-61618", "6310 2Z BALL BEARING 50MM ID 110MM OD 27MM W", "50X110X27 MM, SHIELDED DGBB", "NOS"),
            ("GAIL", "GAIL-BRG-12530", "BALL BEARING, DEEP GROOVE, 6310-ZZ, 50X110X27", "6310 ZZ C3 METALLIC SHIELDED", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "CARB Toroidal Roller Bearing C 2212",
        "ground_truth_id": "BRG-CL-010",
        "records": [
            ("BHEL", "BHEL-88201015", "BRG TOROIDAL ROLLER C 2212 60X110X28", "60X110X28 MM, CARB TOROIDAL ROLLER BEARING", "NOS"),
            ("SAIL", "SAIL-BRG-70740", "TOROIDAL ROLLER BEARING C 2212 (60X110X28)", "60 MM BORE, CARB BEARING SKF EQUIV", "NOS"),
            ("NTPC", "NTPC-BRG-61715", "C 2212 COMPACT ROLLER BEARING 60MM SHAFT", "60X110X28 MM, TOROIDAL ROLLER TYPE", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Cylindrical Roller Bearing NU 314",
        "ground_truth_id": "BRG-CL-011",
        "records": [
            ("BHEL", "BHEL-88201120", "BRG CYL ROLLER NU 314 ECM 70X150X35", "70X150X35 MM, SINGLE ROW CYLINDRICAL ROLLER, BRASS CAGE", "NOS"),
            ("ONGC", "ONGC-B-41630", "BEARING NU-314 CYLINDRICAL ROLLER 70 MM BORE", "70X150X35 MM, HEAVY DUTY ROLLER BEARING", "EA"),
            ("SAIL", "SAIL-BRG-70850", "CYLINDRICAL ROLLER BEARING NU314 (70X150X35)", "70 MM ID, 150 MM OD, 35 MM WIDTH", "NOS"),
            ("NTPC", "NTPC-BRG-61825", "NU 314 ECP ROLLER BEARING 70MM SHAFT", "70X150X35 MM, CYLINDRICAL ROLLER BEARING", "NOS"),
        ]
    },
    {
        "category": "BEARING",
        "name": "Linear Motion Ball Bushing LMK 25 UU",
        "ground_truth_id": "BRG-CL-012",
        "records": [
            ("BHEL", "BHEL-88201210", "LINEAR BRG BUSH LMK 25 UU 25MM SQUARE FLANGE", "25MM SHAFT, SQUARE FLANGED LINEAR BALL BUSHING", "NOS"),
            ("GAIL", "GAIL-BRG-12640", "LINEAR BALL BUSHING, LMK 25 UU, 25 MM SHAFT", "LMK25UU LINEAR MOTION BEARING WITH FLANGE", "NOS"),
            ("NTPC", "NTPC-BRG-61930", "25MM SQUARE FLANGE LINEAR BEARING LMK25UU", "25MM BORE, FLANGED LINEAR BUSH", "NOS"),
        ]
    },

    # =========================================================================
    # CATEGORY: PUMP (~10 clusters + deliberate near-misses)
    # =========================================================================
    {
        "category": "PUMP",
        "name": "Centrifugal End Suction Pump 50 m3/hr 40m Head 15 kW",
        "ground_truth_id": "PMP-CL-001",
        "records": [
            ("BHEL", "BHEL-77300101", "PUMP CENTRIFUGAL END SUCTION 50 M3/HR 40M HEAD 15KW", "FLOW 50 M3/HR, HEAD 40M, 15 KW MOTOR, CI CASING SS IMP", "SET"),
            ("ONGC", "ONGC-P-81010", "END SUCTION CENTRIFUGAL PUMP 50M3/HR @ 40M TDH 15 KW", "CAPACITY: 50 M3/HR, HEAD: 40 METERS, 15KW 3-PHASE MOTOR", "SET"),
            ("GAIL", "GAIL-PMP-20101", "PUMP, CENTRIFUGAL, 50 M3/HR, 40M HEAD, 15 KW MOTOR, CAST IRON", "50 CUBIC M/HR, 40 METERS HEAD, 15 KW 2900 RPM", "SET"),
            ("NTPC", "NTPC-PMP-71020", "50 M3/HR CENTRIFUGAL WATER PUMP 40M HEAD 15KW MOTOR", "50 M3/HR @ 40M, 15 KW INDUCTION MOTOR, CAST IRON/SS", "SET"),
            ("SAIL", "SAIL-PMP-90110", "CENTRIFUGAL WATER PUMP 50 M3/H HEAD 40 MTRS 15 KW", "FLOW: 50 M3/HR, HEAD: 40 M, POWER: 15 KW", "SET"),
        ]
    },
    # DELIBERATE NEAR-MISS 3: Multistage High-Pressure Booster Pump. Same flow (50 m3/hr) but 120m head & 37kW! MUST NOT MERGE!
    {
        "category": "PUMP",
        "name": "Multistage Centrifugal Pump 50 m3/hr 120m Head 37 kW (NEAR MISS)",
        "ground_truth_id": "PMP-NM-001",
        "records": [
            ("BHEL", "BHEL-77300109", "PUMP MULTISTAGE CENTRIFUGAL 50 M3/HR 120M HEAD 37KW", "50 M3/HR, 120M HEAD, 37 KW MOTOR, MULTISTAGE HIGH PRESSURE", "SET"),
            ("ONGC", "ONGC-P-81018", "MULTISTAGE BOOSTER PUMP 50M3/HR @ 120M TDH 37 KW", "50 M3/HR CAPACITY, 120 METERS HEAD, 37KW MOTOR", "SET"),
            ("NTPC", "NTPC-PMP-71029", "HIGH HEAD MULTISTAGE PUMP 50 M3/HR 120M 37KW", "50 M3/HR, HEAD 120M, MOTOR RATING 37 KW", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Positive Displacement Gear Pump 10 LPM 10 Bar Lube Oil",
        "ground_truth_id": "PMP-CL-002",
        "records": [
            ("BHEL", "BHEL-77300215", "PUMP GEAR POSITIVE DISPLACEMENT 10 LPM 10 BAR LUBE OIL", "10 LPM, 10 BAR G, EXTERNAL GEAR PUMP FOR OIL", "NOS"),
            ("ONGC", "ONGC-P-81120", "LUBE OIL ROTARY GEAR PUMP 10 LPM @ 10 KG/CM2", "FLOW 10 LPM, DISCHARGE PR 10 BAR, CI CASING", "SET"),
            ("SAIL", "SAIL-PMP-90225", "10 LPM 10 BAR ROTARY GEAR PUMP FOR LUBRICATION", "10 LITRES/MIN, 10 BAR, GEAR TYPE PD PUMP", "NOS"),
            ("GAIL", "GAIL-PMP-20215", "PUMP, GEAR, 10 LPM, 10 BAR, LUBE OIL TRANSFER", "10 LPM AT 10 BAR PRESSURE, CAST IRON GEARS", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Submersible Dewatering Sump Pump 30 m3/hr 15m Head 3.7 kW",
        "ground_truth_id": "PMP-CL-003",
        "records": [
            ("BHEL", "BHEL-77300320", "PUMP SUBMERSIBLE DEWATERING 30 M3/HR 15M HEAD 3.7KW", "30 M3/HR, 15M HEAD, 3.7 KW (5 HP) SUBMERSIBLE MOTOR", "NOS"),
            ("NTPC", "NTPC-PMP-71230", "30 M3/HR SUBMERSIBLE SUMP PUMP 15M HEAD 3.7 KW", "DISCHARGE 30 M3/HR, HEAD 15 M, 3.7 KW 415V", "SET"),
            ("SAIL", "SAIL-PMP-90335", "DEWATERING SUBMERSIBLE PUMP 30 M3/H HEAD 15M 5HP", "30 M3/HR, 15 METERS, 3.7 KW SUBMERSIBLE MOTOR", "NOS"),
            ("GAIL", "GAIL-PMP-20320", "PUMP, SUBMERSIBLE, SUMP, 30 M3/HR, 15M, 3.7 KW", "30 M3/HR CAPACITY, 15M HEAD, SS CASING", "NOS"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Progressive Cavity Sludge Pump 15 m3/hr 6 Bar",
        "ground_truth_id": "PMP-CL-004",
        "records": [
            ("BHEL", "BHEL-77300410", "PUMP PROGRESSIVE CAVITY SCREW 15 M3/HR 6 BAR NITRILE", "15 M3/HR, 6 BAR, SINGLE SCREW PROGRESSIVE CAVITY", "SET"),
            ("ONGC", "ONGC-P-81230", "PROGRESSIVE CAVITY SLUDGE PUMP 15 M3/HR 6 KG/CM2", "15 M3/HR, 6 BAR G, NITRILE STATOR SS ROTOR", "SET"),
            ("SAIL", "SAIL-PMP-90440", "15 M3/HR 6 BAR PC SCREW PUMP FOR SLUDGE HANDLING", "15 CUBIC M/HR, 6 BAR, HELICAL ROTOR STATOR", "SET"),
            ("NTPC", "NTPC-PMP-71340", "EFFLUENT PROGRESSIVE CAVITY PUMP 15 M3/HR 6 BAR", "15 M3/HR @ 6 BAR, ETP SLUDGE PUMP", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Vertical Turbine Cooling Water Pump 500 m3/hr 25m Head 55 kW",
        "ground_truth_id": "PMP-CL-005",
        "records": [
            ("BHEL", "BHEL-77300525", "PUMP VERTICAL TURBINE 500 M3/HR 25M HEAD 55KW CW", "500 M3/HR, 25M HEAD, 55 KW MOTOR, VERTICAL WET PIT", "SET"),
            ("NTPC", "NTPC-PMP-71450", "VERTICAL TURBINE COOLING WATER PUMP 500 M3/HR 25M 55KW", "500 M3/HR @ 25M, 55 KW, SUSPENDED LENGTH 4M", "SET"),
            ("SAIL", "SAIL-PMP-90550", "500 M3/H 25M HEAD VERTICAL TURBINE PUMP 55 KW", "CAPACITY 500 M3/HR, HEAD 25M, 55 KW MOTOR", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Diaphragm Chemical Dosing Pump 0-50 LPH 8 Bar PTFE",
        "ground_truth_id": "PMP-CL-006",
        "records": [
            ("BHEL", "BHEL-77300615", "PUMP DOSING DIAPHRAGM 50 LPH 8 BAR PTFE HEAD", "0-50 LPH, 8 BAR, PTFE DIAPHRAGM, CHEMICAL METERING", "NOS"),
            ("ONGC", "ONGC-P-81345", "CHEMICAL INJECTION DIAPHRAGM PUMP 50 LPH @ 8 BAR PTFE", "50 LITRES/HR, 8 BAR, ELECTRONIC DOSING", "EA"),
            ("GAIL", "GAIL-PMP-20430", "PUMP, CHEMICAL DOSING, 50 LPH, 8 BAR, PTFE DIAPHRAGM", "0-50 LPH VARIABLE STROKE, 8 BAR G", "NOS"),
            ("NTPC", "NTPC-PMP-71560", "50 LPH 8 BAR PTFE DIAPHRAGM CHEMICAL METERING PUMP", "50 LPH, 8 BAR, MOTOR DRIVEN DIAPHRAGM", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Boiler Feed Water High Pressure Pump 80 m3/hr 350m Head",
        "ground_truth_id": "PMP-CL-007",
        "records": [
            ("BHEL", "BHEL-77300730", "PUMP BOILER FEED BFP 80 M3/HR 350M HEAD 110KW", "80 M3/HR, 350M HEAD, 110 KW MOTOR, MULTISTAGE RING SECTION", "SET"),
            ("NTPC", "NTPC-PMP-71670", "BOILER FEED WATER PUMP 80 M3/HR 350M HEAD 110 KW", "80 M3/HR @ 350M TDH, BFP MULTISTAGE FOR HIGH PR STEAM", "SET"),
            ("SAIL", "SAIL-PMP-90660", "BFP MULTISTAGE PUMP 80 M3/H 350M 110 KW FEED WATER", "80 M3/HR, HEAD 350 M, 110 KW MOTOR", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Horizontal Split Case Fire Water Pump 2000 GPM 10 Bar",
        "ground_truth_id": "PMP-CL-008",
        "records": [
            ("BHEL", "BHEL-77300820", "PUMP HORIZONTAL SPLIT CASE FIRE 2000 GPM 10 BAR", "2000 GPM (454 M3/HR), 10 BAR (100M HEAD), DIESEL/MOTOR", "SET"),
            ("ONGC", "ONGC-P-81460", "HORIZONTAL SPLIT CASE FIRE WATER PUMP 2000 GPM @ 10 BAR", "2000 US GPM, 10 BAR DISCHARGE PRESSURE, HSC", "SET"),
            ("GAIL", "GAIL-PMP-20540", "PUMP, FIRE WATER, SPLIT CASE, 2000 GPM, 10 BAR", "454 M3/HR (2000 GPM), 100M HEAD, DUAL SUCTION HSC", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Reciprocating Triplex Plunger Pump 50 LPM 150 Bar",
        "ground_truth_id": "PMP-CL-009",
        "records": [
            ("BHEL", "BHEL-77300910", "PUMP TRIPLEX PLUNGER HIGH PR 50 LPM 150 BAR", "50 LPM, 150 BAR G, CERAMIC PLUNGERS, SS HEAD", "SET"),
            ("ONGC", "ONGC-P-81570", "HIGH PRESSURE TRIPLEX PLUNGER PUMP 50 LPM @ 150 BAR", "50 LITRES/MIN, 150 KG/CM2, RECIPROCATING", "SET"),
            ("SAIL", "SAIL-PMP-90770", "50 LPM 150 BAR TRIPLEX HIGH PRESSURE PLUNGER PUMP", "FLOW 50 LPM, PR 150 BAR, PLUNGER TYPE", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Liquid Ring Vacuum Pump 100 m3/hr 33 mbar",
        "ground_truth_id": "PMP-CL-010",
        "records": [
            ("BHEL", "BHEL-77301015", "PUMP LIQUID RING VACUUM LRVP 100 M3/HR 33 MBAR", "100 M3/HR SUCTION, 33 MBAR ABSOLUTE, CI BODY BRONZE ROTOR", "SET"),
            ("GAIL", "GAIL-PMP-20650", "PUMP, VACUUM, LIQUID RING, 100 M3/HR, 33 MBAR ABS", "100 M3/HR, ULTIMATE VACUUM 33 MBAR, WATER SEALED", "SET"),
            ("SAIL", "SAIL-PMP-90880", "100 M3/HR LIQUID RING VACUUM PUMP (33 MBAR)", "SUCTION CAPACITY 100 M3/HR, CAST IRON LRVP", "NOS"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Submersible Borewell Turbine Pump 25 m3/hr 120m Head 11 kW",
        "ground_truth_id": "PMP-CL-011",
        "records": [
            ("BHEL", "BHEL-77301120", "PUMP BOREWELL SUBMERSIBLE 25 M3/HR 120M HEAD 11KW", "25 M3/HR, 120M HEAD, 11 KW 15HP 415V MULTISTAGE SUBMERSIBLE", "SET"),
            ("NTPC", "NTPC-PMP-71780", "25 M3/HR 120M HEAD BOREWELL PUMP 11 KW MOTOR", "FLOW: 25 M3/HR, HEAD: 120 M, 11 KW SUBMERSIBLE MOTOR", "SET"),
            ("SAIL", "SAIL-PMP-90990", "DEEP WELL SUBMERSIBLE PUMP 25 M3/H 120M 15 HP", "25 M3/HR @ 120M HEAD, 11 KW WATER COOLED", "SET"),
            ("ONGC", "ONGC-P-81680", "SUBMERSIBLE BOREWELL WATER PUMP 25 M3/HR @ 120M TDH", "25 M3/HR, 120 METERS, 11 KW 3-PHASE", "SET"),
        ]
    },
    {
        "category": "PUMP",
        "name": "Chemical Canned Motor Pump 15 m3/hr 30m Head Hastelloy",
        "ground_truth_id": "PMP-CL-012",
        "records": [
            ("BHEL", "BHEL-77301230", "PUMP CANNED MOTOR SEALLESS 15 M3/HR 30M HASTELLOY", "15 M3/HR, 30M HEAD, SEALLESS ZERO LEAKAGE, HASTELLOY-C", "SET"),
            ("GAIL", "GAIL-PMP-20760", "PUMP, CANNED MOTOR, SEALLESS, 15 M3/HR, 30M, HASTELLOY", "15 M3/HR @ 30M, HAST-C CASING, CORROSIVE SERVICE", "SET"),
            ("ONGC", "ONGC-P-81790", "SEALLESS CANNED MOTOR PUMP 15 M3/HR @ 30M TDH", "15 M3/HR, 30M HEAD, 5.5 KW, ZERO EMISSION", "EA"),
        ]
    },

    # =========================================================================
    # CATEGORY: FLANGE (~10 clusters + deliberate near-misses)
    # =========================================================================
    {
        "category": "FLANGE",
        "name": "Weld Neck Flange 6in Class 150 ASME B16.5 A105",
        "ground_truth_id": "FLG-CL-001",
        "records": [
            ("BHEL", "BHEL-66100101", "FLG WNRF 6IN 150# A105 SCH40 ASME B16.5", "SIZE: 6 INCH, RATING: 150 LB, WELD NECK RAISED FACE, A105 CS", "NOS"),
            ("ONGC", "ONGC-F-31010", "6\" WELD NECK FLANGE CLASS-150 RF ASME B16.5 A105 SCH 40", "6 INCH NB, 150 LBS RF, WNRF ASTM A105 FORGED CS", "EA"),
            ("GAIL", "GAIL-FLG-40101", "FLANGE, WELD NECK, RAISED FACE, 6\", 150#, CS A105, SCH 40", "6 INCH (150MM), ASME B16.5 150 LBS, WELDING NECK", "NOS"),
            ("NTPC", "NTPC-FLG-81020", "WNRF FLANGE 150MM NB 150 CLASS ASTM A105 SCH 40", "150MM NB, CLASS 150 RF, WELD NECK FLANGE", "NOS"),
            ("SAIL", "SAIL-FLG-50110", "FORGED CARBON STEEL WELD NECK FLANGE 6\" 150 LBS RF", "6\" NB, ASME B16.5, CLASS 150, A105 WNRF SCH 40", "NOS"),
        ]
    },
    # DELIBERATE NEAR-MISS 4: Slip-On Flange (SORF) with same size & rating. MUST NOT MERGE with Weld Neck Flange (WNRF)!
    {
        "category": "FLANGE",
        "name": "Slip-On Flange 6in Class 150 ASME B16.5 A105 (NEAR MISS to WNRF)",
        "ground_truth_id": "FLG-NM-001",
        "records": [
            ("BHEL", "BHEL-66100109", "FLG SORF 6IN 150# A105 ASME B16.5", "SIZE: 6 INCH, RATING: 150 LB, SLIP ON RAISED FACE, A105 CS", "NOS"),
            ("ONGC", "ONGC-F-31019", "6\" SLIP ON FLANGE CLASS-150 RF ASME B16.5 A105", "6 INCH NB, 150 LBS RF, SORF ASTM A105 SLIP ON", "EA"),
            ("GAIL", "GAIL-FLG-40109", "FLANGE, SLIP ON, RAISED FACE, 6\", 150#, CS A105", "6 INCH (150MM), ASME B16.5 150 LBS, SLIP ON", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Blind Flange 4in Class 300 ASME B16.5 A105",
        "ground_truth_id": "FLG-CL-002",
        "records": [
            ("BHEL", "BHEL-66100215", "FLG BLRF 4IN 300# A105 ASME B16.5", "SIZE 4\", 300 LB, BLIND RAISED FACE, ASTM A105", "NOS"),
            ("ONGC", "ONGC-F-31125", "4\" BLIND FLANGE CLASS-300 RF ASME B16.5 A105", "4 INCH (100MM NB), 300#, FORGED CS BLIND", "EA"),
            ("SAIL", "SAIL-FLG-50220", "BLIND FLANGE 4\" ASME CLASS 300 RF ASTM A105", "4 INCH NB, CLASS 300 BLRF, FORGED STEEL", "NOS"),
            ("NTPC", "NTPC-FLG-81130", "BLRF FLANGE 100MM NB 300 CLASS ASTM A105", "100MM, CLASS 300, BLIND FLANGE RAISED FACE", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Slip-On Raised Face Flange 3in Class 150 SS304",
        "ground_truth_id": "FLG-CL-003",
        "records": [
            ("BHEL", "BHEL-66100320", "FLG SORF 3IN 150# SS304 ASTM A182 F304", "SIZE 3\", 150 LBS, SLIP ON RF, STAINLESS STEEL 304", "NOS"),
            ("GAIL", "GAIL-FLG-40215", "FLANGE, SLIP ON, 3 INCH, 150#, SS 304, ASME B16.5 RF", "80 MM NB, CLASS 150, SS304 / A182", "NOS"),
            ("ONGC", "ONGC-F-31230", "3\" SS-304 SLIP ON FLANGE CLASS 150 RF", "3 INCH, 150 LBS RF, STAINLESS STEEL 304", "EA"),
            ("SAIL", "SAIL-FLG-50335", "STAINLESS STEEL SLIP-ON FLANGE 3\" 150# RF SS304", "80MM NB (3\"), CLASS 150, A182 F304 SORF", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Socket Weld Flange 2in Class 600 ASME B16.5 A105",
        "ground_truth_id": "FLG-CL-004",
        "records": [
            ("BHEL", "BHEL-66100412", "FLG SWRF 2IN 600# A105 ASME B16.5", "2 INCH, 600 LB, SOCKET WELD RAISED FACE, A105", "NOS"),
            ("ONGC", "ONGC-F-31340", "2\" SOCKET WELD FLANGE CLASS-600 RF A105", "50 MM NB, 600 LBS RF, SWRF FORGED CARBON STEEL", "EA"),
            ("NTPC", "NTPC-FLG-81240", "SWRF FLANGE 50MM NB 600 CLASS ASTM A105", "50MM, CLASS 600, SOCKET WELD FLANGE RF", "NOS"),
            ("GAIL", "GAIL-FLG-40325", "FLANGE, SOCKET WELD, 2 INCH, 600#, CS A105", "2\", ASME B16.5 CL 600 RF, ASTM A105", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Lap Joint Flange with Stub End 4in Class 150 CS",
        "ground_truth_id": "FLG-CL-005",
        "records": [
            ("BHEL", "BHEL-66100518", "FLG LAP JOINT 4IN 150# A105 WITH STUB END", "4 INCH, 150 LBS, LAP JOINT FLANGE WITH TYPE A STUB END", "NOS"),
            ("GAIL", "GAIL-FLG-40430", "FLANGE, LAP JOINT, 4\", 150#, CARBON STEEL A105", "100MM NB, CLASS 150, LJ FLANGE FOR STUB END", "NOS"),
            ("SAIL", "SAIL-FLG-50445", "4\" CS LAP JOINT FLANGE CLASS 150 ASME B16.5", "4 INCH, 150 LBS, FORGED CARBON STEEL A105", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Threaded Companion Flange 1.5in Class 300 NPT A105",
        "ground_truth_id": "FLG-CL-006",
        "records": [
            ("BHEL", "BHEL-66100622", "FLG THREADED NPT 1.5IN 300# A105 RF B16.5", "1-1/2 INCH, 300 LBS, NPT FEMALE THREADED, A105", "NOS"),
            ("ONGC", "ONGC-F-31450", "1.5\" SCREWED THREADED FLANGE CLASS-300 RF A105", "40 MM NB, 300 LBS RF, NPT THREAD FORGED CS", "EA"),
            ("NTPC", "NTPC-FLG-81350", "THREADED FLANGE 40MM NB 300 CLASS NPT ASTM A105", "40MM (1.5\"), CLASS 300 RF, SCREWED FLANGE", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Plate Flange Table E 8in BS 10 Mild Steel",
        "ground_truth_id": "FLG-CL-007",
        "records": [
            ("BHEL", "BHEL-66100715", "FLG PLATE TABLE E 8IN BS 10 MS FLAT FACE", "200MM NB, BS 10 TABLE E, MILD STEEL PLATE SLIP ON", "NOS"),
            ("SAIL", "SAIL-FLG-50560", "PLATE FLANGE 8\" TABLE E BS 10 MILD STEEL", "8 INCH, TABLE E, MS PLATE FLANGE IS 2062", "NOS"),
            ("NTPC", "NTPC-FLG-81460", "8\" MS PLATE FLANGE TABLE-E FLAT FACE BS10", "200 MM NB, BS 10 TABLE E, MS FF", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Spectacle Blind Flange 6in Class 150 RF ASME B16.48 CS",
        "ground_truth_id": "FLG-CL-008",
        "records": [
            ("BHEL", "BHEL-66100820", "SPECTACLE BLIND 6IN 150# RF ASME B16.48 A516 GR70", "6 INCH, 150 LBS RF, FIGURE 8 SPECTACLE BLIND", "NOS"),
            ("ONGC", "ONGC-F-31560", "6\" SPECTACLE BLIND FLANGE CLASS-150 ASME B16.48 CS", "6 INCH NB, 150#, ASTM A516 GR 70 / A105", "EA"),
            ("GAIL", "GAIL-FLG-40540", "SPECTACLE BLIND, 6 INCH, CLASS 150, CS ASME B16.48", "6\", 150 LBS RF, CARBON STEEL FIGURE 8", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Orifice Flange Union Pair 4in Class 300 WNRF A105",
        "ground_truth_id": "FLG-CL-009",
        "records": [
            ("BHEL", "BHEL-66100912", "ORIFICE FLANGE PAIR 4IN 300# WNRF A105 JACK SCREWS", "4 INCH, 300 LBS, WNRF PAIR WITH PRESSURE TAPS & SCREWS", "PAIR"),
            ("GAIL", "GAIL-FLG-40650", "ORIFICE FLANGES (PAIR), 4\", 300#, WNRF, A105 CS", "100MM NB, CLASS 300, ORIFICE UNION ASME B16.36", "PAIR"),
            ("NTPC", "NTPC-FLG-81570", "4\" ORIFICE FLANGE ASSEMBLY 300 CLASS WNRF CS", "4 INCH, 300 LBS, WNRF PAIR WITH JACKING SCREWS", "PAIR"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "RTJ Weld Neck Flange 8in Class 900 ASTM A182 F11",
        "ground_truth_id": "FLG-CL-010",
        "records": [
            ("BHEL", "BHEL-66101025", "FLG WNRF RTJ 8IN 900# ALLOY STEEL A182 F11 SCH80", "8 INCH, 900 LB, RING TYPE JOINT (RTJ), ALLOY STEEL F11", "NOS"),
            ("ONGC", "ONGC-F-31670", "8\" WELD NECK FLANGE CLASS-900 RTJ ALLOY STEEL F11", "200 MM NB, 900 LBS, RTJ GROOVE, ASTM A182 F11", "EA"),
            ("SAIL", "SAIL-FLG-50675", "8\" RTJ WNRF FLANGE CLASS 900 ALLOY STEEL F11", "8 INCH NB, CLASS 900 RTJ, ALLOY STEEL", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Swivel Ring Flange 6in Class 600 ASME B16.5 A105",
        "ground_truth_id": "FLG-CL-011",
        "records": [
            ("BHEL", "BHEL-66101130", "SWIVEL RING FLG 6IN 600# A105 SUBSEA ROTATABLE", "6 INCH, CLASS 600, TWO-PIECE SWIVEL RING FLANGE, A105", "NOS"),
            ("ONGC", "ONGC-F-31780", "6\" SWIVEL FLANGE CLASS-600 RF ASME B16.5 A105", "6 INCH NB, 600#, ROTATABLE OUTER RING FOR OFFSHORE", "EA"),
            ("GAIL", "GAIL-FLG-40760", "FLANGE, SWIVEL RING, 6\", 600 LBS, CS A105", "6 INCH, 600#, SWIVEL ALIGNMENT FLANGE", "NOS"),
        ]
    },
    {
        "category": "FLANGE",
        "name": "Reducing Flange 4in x 2in Class 150 RF CS A105",
        "ground_truth_id": "FLG-CL-012",
        "records": [
            ("BHEL", "BHEL-66101240", "REDUCING FLG 4IN X 2IN 150# A105 RF ASME B16.5", "SIZE 4\" X 2\", CLASS 150 RAISED FACE, A105 FORGED CS", "NOS"),
            ("NTPC", "NTPC-FLG-81680", "4\" X 2\" CS REDUCING FLANGE 150 CLASS RF ASTM A105", "100MM X 50MM NB, CLASS 150 RF REDUCING FLANGE", "NOS"),
            ("SAIL", "SAIL-FLG-50785", "4 INCH TO 2 INCH REDUCING FLANGE CLASS 150 RF CS", "4\" X 2\" ASME B16.5 150#, ASTM A105", "NOS"),
            ("GAIL", "GAIL-FLG-40870", "FLANGE, REDUCING, 4\" X 2\", 150#, CS A105 RF", "100MM X 50MM, CLASS 150, FORGED CARBON STEEL", "NOS"),
        ]
    },
]


def generate_seed_data(output_csv_path: str):
    """
    Generates the CSV file containing ~180-200 synthetic CPSE records.
    Columns: cpse,material_code,description,specification,unit,category,ground_truth_cluster
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    
    rows = []
    total_records = 0
    categories_count = {}
    cpse_count = {}

    for cluster in CLUSTERS_DATA:
        category = cluster["category"]
        gt_id = cluster["ground_truth_id"]
        for cpse, code, desc, spec, unit in cluster["records"]:
            rows.append({
                "cpse": cpse,
                "material_code": code,
                "description": desc,
                "specification": spec,
                "unit": unit,
                "category": category,
                "ground_truth_cluster": gt_id
            })
            total_records += 1
            categories_count[category] = categories_count.get(category, 0) + 1
            cpse_count[cpse] = cpse_count.get(cpse, 0) + 1

    fieldnames = ["cpse", "material_code", "description", "specification", "unit", "category", "ground_truth_cluster"]
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {total_records} synthetic CPSE records.")
    print(f"Output saved to: {output_csv_path}")
    print("Breakdown by Category:", categories_count)
    print("Breakdown by CPSE:", cpse_count)
    print(f"Total equivalence clusters + deliberate near-misses: {len(CLUSTERS_DATA)}")
    return rows


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_csv = os.path.join(current_dir, "cpse_seed.csv")
    generate_seed_data(target_csv)
