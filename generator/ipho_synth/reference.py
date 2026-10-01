"""Reference data used to make the synthetic IPHO data realistic.

Everything here is either public geography or generic clinical vocabulary.
No row in this file (or anything generated from it) describes a real person.
"""

# Zamboanga Sibugay municipalities with a rough population weight. Ipil is the
# provincial capital and where the IPHO and its outpatient clinic sit, so it
# dominates clinic traffic.
MUNICIPALITIES: dict[str, float] = {
    "Ipil": 0.22,
    "Kabasalan": 0.08,
    "Titay": 0.07,
    "Siay": 0.07,
    "Naga": 0.06,
    "Diplahan": 0.05,
    "Buug": 0.05,
    "Imelda": 0.05,
    "Alicia": 0.05,
    "Tungawan": 0.05,
    "Roseller T. Lim": 0.05,
    "Malangas": 0.04,
    "Payao": 0.04,
    "Olutanga": 0.04,
    "Mabuhay": 0.04,
    "Talusan": 0.04,
}

# (code_suffix, description, unit_of_measure, unit_price_php, therapeutic_class, base_daily_demand)
MEDICINES: list[tuple[str, str, str, float, str, float]] = [
    ("001", "Paracetamol 500 mg tablet", "tablet", 0.85, "analgesic", 260),
    ("002", "Paracetamol 250 mg/5 mL syrup, 60 mL", "bottle", 28.0, "analgesic", 18),
    ("003", "Ibuprofen 400 mg tablet", "tablet", 1.40, "analgesic", 60),
    ("004", "Mefenamic Acid 500 mg capsule", "capsule", 1.10, "analgesic", 70),
    ("005", "Amoxicillin 500 mg capsule", "capsule", 2.10, "antibiotic", 180),
    ("006", "Amoxicillin 250 mg/5 mL suspension, 60 mL", "bottle", 35.0, "antibiotic", 14),
    ("007", "Co-amoxiclav 625 mg tablet", "tablet", 12.50, "antibiotic", 30),
    ("008", "Cefalexin 500 mg capsule", "capsule", 3.20, "antibiotic", 45),
    ("009", "Cotrimoxazole 800/160 mg tablet", "tablet", 1.80, "antibiotic", 40),
    ("010", "Azithromycin 500 mg tablet", "tablet", 18.0, "antibiotic", 12),
    ("011", "Ciprofloxacin 500 mg tablet", "tablet", 2.60, "antibiotic", 25),
    ("012", "Metronidazole 500 mg tablet", "tablet", 1.30, "antibiotic", 35),
    ("013", "Doxycycline 100 mg capsule", "capsule", 2.40, "antibiotic", 20),
    ("014", "Amlodipine 5 mg tablet", "tablet", 0.95, "cardiovascular", 210),
    ("015", "Amlodipine 10 mg tablet", "tablet", 1.25, "cardiovascular", 90),
    ("016", "Losartan 50 mg tablet", "tablet", 1.60, "cardiovascular", 190),
    ("017", "Metoprolol 50 mg tablet", "tablet", 1.10, "cardiovascular", 60),
    ("018", "Hydrochlorothiazide 25 mg tablet", "tablet", 0.70, "cardiovascular", 50),
    ("019", "Simvastatin 20 mg tablet", "tablet", 1.90, "cardiovascular", 80),
    ("020", "Aspirin 80 mg tablet", "tablet", 0.60, "cardiovascular", 70),
    ("021", "Metformin 500 mg tablet", "tablet", 0.80, "antidiabetic", 220),
    ("022", "Gliclazide 80 mg tablet", "tablet", 1.50, "antidiabetic", 70),
    ("023", "Oral Rehydration Salts, 20.5 g sachet", "sachet", 6.50, "gastrointestinal", 40),
    ("024", "Zinc Sulfate 20 mg/5 mL syrup, 60 mL", "bottle", 42.0, "gastrointestinal", 8),
    ("025", "Loperamide 2 mg capsule", "capsule", 0.90, "gastrointestinal", 20),
    ("026", "Omeprazole 20 mg capsule", "capsule", 1.70, "gastrointestinal", 55),
    ("027", "Albendazole 400 mg chewable tablet", "tablet", 3.10, "anthelmintic", 25),
    ("028", "Mebendazole 500 mg tablet", "tablet", 2.80, "anthelmintic", 10),
    ("029", "Salbutamol 2 mg tablet", "tablet", 0.50, "respiratory", 50),
    ("030", "Salbutamol nebule 2.5 mg/2.5 mL", "nebule", 9.50, "respiratory", 30),
    ("031", "Cetirizine 10 mg tablet", "tablet", 0.75, "respiratory", 65),
    ("032", "Carbocisteine 500 mg capsule", "capsule", 1.60, "respiratory", 45),
    ("033", "Ascorbic Acid 500 mg tablet", "tablet", 0.55, "vitamin", 150),
    ("034", "Ferrous Sulfate + Folic Acid tablet", "tablet", 0.65, "vitamin", 95),
    ("035", "Vitamin A 200,000 IU capsule", "capsule", 4.50, "vitamin", 12),
    ("036", "Multivitamins syrup, 120 mL", "bottle", 55.0, "vitamin", 6),
    ("037", "Isoniazid + Rifampicin FDC tablet", "tablet", 6.80, "tb_program", 40),
    ("038", "Ethambutol 400 mg tablet", "tablet", 2.20, "tb_program", 15),
    ("039", "Povidone-Iodine 10% solution, 120 mL", "bottle", 85.0, "supply", 3),
    ("040", "Sterile Gauze Pad 4x4, pack of 10", "pack", 45.0, "supply", 6),
    ("041", "Disposable Syringe 3 mL", "piece", 4.50, "supply", 40),
    ("042", "Surgical Face Mask", "piece", 2.00, "supply", 90),
    ("043", "Examination Gloves, medium", "pair", 6.00, "supply", 50),
    ("044", "Alcohol 70% isopropyl, 500 mL", "bottle", 75.0, "supply", 5),
    ("045", "Dengue NS1 Rapid Test Kit", "kit", 220.0, "diagnostic", 4),
    ("046", "Malaria Rapid Diagnostic Test", "kit", 95.0, "diagnostic", 2),
    ("047", "Lagundi 600 mg tablet", "tablet", 2.10, "respiratory", 40),
    ("048", "Insulin NPH 100 IU/mL, 10 mL vial", "vial", 480.0, "antidiabetic", 1.5),
]

# Multiplier per therapeutic class per calendar month (1..12). Rainy season in
# Mindanao (roughly June–October) pushes up fever, diarrhoea and respiratory
# illness; anthelmintics spike with the January/July school deworming rounds.
_FLAT = [1.0] * 12
SEASONALITY: dict[str, list[float]] = {
    "analgesic":        [1.0, 0.9, 0.9, 0.9, 1.0, 1.25, 1.4, 1.45, 1.35, 1.2, 1.0, 1.0],
    "antibiotic":       [1.1, 1.0, 0.9, 0.85, 0.9, 1.1, 1.25, 1.3, 1.25, 1.1, 1.0, 1.1],
    "gastrointestinal": [0.9, 0.85, 0.9, 1.0, 1.1, 1.4, 1.6, 1.6, 1.4, 1.2, 1.0, 0.9],
    "respiratory":      [1.3, 1.2, 1.0, 0.85, 0.85, 1.1, 1.25, 1.3, 1.2, 1.1, 1.15, 1.3],
    "anthelmintic":     [3.0, 0.6, 0.5, 0.5, 0.5, 0.6, 3.0, 0.6, 0.5, 0.5, 0.5, 0.6],
    "diagnostic":       [0.8, 0.7, 0.7, 0.8, 1.0, 1.5, 1.9, 2.0, 1.7, 1.3, 1.0, 0.8],
    "cardiovascular":   _FLAT,
    "antidiabetic":     _FLAT,
    "vitamin":          _FLAT,
    "tb_program":       _FLAT,
    "supply":           _FLAT,
}

FUND_SOURCES = ["DOH", "DOH", "LGU", "LGU", "PhilHealth", "Donation"]
STORE_ROOMS = ["Main Warehouse", "Main Warehouse", "Storeroom A", "Storeroom B"]

# Clinic diagnoses. Each canonical diagnosis has free-text variants the way an
# encoder would actually type them — the dbt layer maps these back via a seed.
# (canonical, [variants], therapeutic classes typically dispensed, monthly seasonality key)
DIAGNOSES: list[tuple[str, list[str], list[str], str]] = [
    ("Acute upper respiratory infection",
     ["URTI", "uri", "Upper respiratory tract infection", "Acute URTI", "colds"],
     ["analgesic", "respiratory", "vitamin"], "respiratory"),
    ("Essential hypertension",
     ["HPN", "Hypertension", "hypertension stage 1", "HTN", "high blood"],
     ["cardiovascular"], "flat"),
    ("Type 2 diabetes mellitus",
     ["DM type 2", "T2DM", "Diabetes", "DM2"],
     ["antidiabetic"], "flat"),
    ("Acute gastroenteritis",
     ["AGE", "acute gastro", "Diarrhea", "LBM", "Acute Gastroenteritis"],
     ["gastrointestinal"], "gastrointestinal"),
    ("Dengue fever",
     ["Dengue", "dengue fever", "DF", "Suspected dengue"],
     ["analgesic", "diagnostic"], "diagnostic"),
    ("Urinary tract infection",
     ["UTI", "Urinary tract infection", "uti"],
     ["antibiotic"], "antibiotic"),
    ("Community-acquired pneumonia",
     ["CAP", "Pneumonia", "CAP-low risk"],
     ["antibiotic", "respiratory"], "respiratory"),
    ("Bronchial asthma",
     ["BA", "Asthma", "bronchial asthma in exacerbation"],
     ["respiratory"], "respiratory"),
    ("Pulmonary tuberculosis",
     ["PTB", "Pulmonary TB", "TB"],
     ["tb_program"], "flat"),
    ("Skin and soft tissue infection",
     ["Wound infection", "Infected wound", "Cellulitis", "Boil"],
     ["antibiotic", "supply"], "flat"),
    ("Iron-deficiency anaemia",
     ["Anemia", "IDA", "anemia, mild"],
     ["vitamin"], "flat"),
    ("Intestinal helminthiasis",
     ["Helminthiasis", "Worm infestation", "Parasitism"],
     ["anthelmintic"], "anthelmintic"),
]

DIAGNOSIS_WEIGHTS = [0.24, 0.17, 0.10, 0.10, 0.06, 0.07, 0.05, 0.04, 0.03, 0.06, 0.04, 0.04]

FIRST_NAMES_F = ["Maria", "Ana", "Rosalie", "Jocelyn", "Liza", "Grace", "Cristina", "Angelica",
                 "Jasmine", "Nenita", "Marites", "Divina", "Rowena", "Shiela", "Kristine", "Aileen",
                 "Mary Joy", "Lorna", "Evelyn", "Fatima", "Nur-aisa", "Princess", "Rhea", "Leah"]
FIRST_NAMES_M = ["Jose", "Juan", "Mark", "John Paul", "Ramil", "Rodel", "Arnel", "Jun", "Romeo",
                 "Ricardo", "Christian", "Jerome", "Alvin", "Rogelio", "Danilo", "Abdul",
                 "Mohammad", "Kevin", "Jayson", "Ernesto", "Edgar", "Reynaldo", "Jomar", "Benjie"]
LAST_NAMES = ["Dela Cruz", "Santos", "Reyes", "Garcia", "Mendoza", "Torres", "Flores", "Ramos",
              "Villanueva", "Castillo", "Aquino", "Bautista", "Gonzales", "Fernandez", "Lopez",
              "Navarro", "Salazar", "Abubakar", "Hassan", "Tan", "Lim", "Alonzo", "Cabahug",
              "Ebarle", "Pacaña", "Lumapas", "Sarmiento", "Macaraeg", "Dagondon", "Omar"]
BARANGAY_SUFFIXES = ["Poblacion", "Sanito", "Taway", "Bangkerohan", "Lower Taway", "Don Andres",
                     "Magdaup", "Tiayon", "Upper Pangi", "Lumbia", "Bacalan", "Tenan"]
CIVIL_STATUS = ["Single", "Married", "Married", "Widowed", "Separated"]
OCCUPATIONS = ["Farmer", "Fisherfolk", "Housewife", "Vendor", "Student", "Driver", "Teacher",
               "Government employee", "Unemployed", "Laborer", "Retired", ""]
CLINIC_STAFF = ["nurse.alvarez@ipho.example", "nurse.cabrera@ipho.example",
                "dr.mangubat@ipho.example", "midwife.saldua@ipho.example"]
