import pandas as pd
from pathlib import Path


INPUT_FILES = ["2023.csv", "2024.csv"] 
OUTPUT_FILE = "people_14_25_2023_2024_fullvars.csv"
AGE_MIN, AGE_MAX = 14, 25             


UF_SIGLA = {
    11:"RO", 12:"AC", 13:"AM", 14:"RR", 15:"PA", 16:"AP", 17:"TO", 21:"MA", 22:"PI", 23:"CE", 24:"RN", 25:"PB", 26:"PE", 27:"AL", 28:"SE", 29:"BA",
    31:"MG", 32:"ES", 33:"RJ", 35:"SP", 41:"PR", 42:"SC", 43:"RS", 50:"MS", 51:"MT", 52:"GO", 53:"DF"
}
UF_NAME = {
    11:"Rondônia", 12:"Acre", 13:"Amazonas", 14:"Roraima", 15:"Pará", 16:"Amapá", 17:"Tocantins",
    21:"Maranhão", 22:"Piauí", 23:"Ceará", 24:"Rio Grande do Norte", 25:"Paraíba", 26:"Pernambuco",
    27:"Alagoas", 28:"Sergipe", 29:"Bahia", 31:"Minas Gerais", 32:"Espírito Santo", 33:"Rio de Janeiro", 35:"São Paulo",
    41:"Paraná", 42:"Santa Catarina", 43:"Rio Grande do Sul",
    50:"Mato Grosso do Sul", 51:"Mato Grosso", 52:"Goiás", 53:"Distrito Federal"
}

AREA_MAP = {1: "Urban", 2: "Rural"}                           # V1022
SEX_MAP  = {1: "Male",  2: "Female"}                          # V2007
RACE_MAP = {1: "White", 2: "Black", 3: "Asian",
            4: "Pardo", 5: "Indigenous", 9: "Unknown"}   # V2010
SCHOOL_MAP = {1: "Yes", 2: "No"}                               # V3002
OCC_MAP    = {1: "Employed", 2: "Unemployed", 3: "Out of labor force"}  # VD4002
CONTR_MAP  = {1: "Yes", 2: "No"}                               # V4032 (applies only if employed)

# Keep only required columns if present
USECOLS = [
    "ano","trimestre","id_uf","V1022","V2007","V2009","V2010","V3002",
    "VD4002","V4032","VD4019","V1028"
]

# ---------------------------
# 2) LOADER
# ---------------------------
def load_one_csv(path: str) -> pd.DataFrame:
    # Read header to decide available columns
    header = pd.read_csv(path, nrows=0).columns.tolist()
    use = [c for c in USECOLS if c in header]

    df = pd.read_csv(path, usecols=use, low_memory=False)

    # Standardize types where applicable
    int_cols = ["ano","trimestre","id_uf","V1022","V2007","V2009","V2010","V3002","VD4002","V4032"]
    for c in int_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    if "VD4019" in df.columns:
        df["VD4019"] = pd.to_numeric(df["VD4019"], errors="coerce")  # income can be float
    if "V1028" in df.columns:
        df["V1028"] = pd.to_numeric(df["V1028"], errors="coerce")    # weight may be float

    # Rename core vars to readable names (keep originals too)
    df = df.rename(columns={
        "ano": "Year",
        "trimestre": "Quarter",
        "id_uf": "id_uf",
        "V1022": "Area_code",
        "V2007": "Sex_code",
        "V2009": "Age",
        "V2010": "Race_code",
        "V3002": "School_code",
        "VD4002": "Occupation_code",
        "V4032": "Contributor_code",
        "VD4019": "Income_all_jobs",
        "V1028": "Weight_V1028"
    })

    # Labels
    df["UF"] = df["id_uf"].map(UF_SIGLA)
    df["UF_name"] = df["id_uf"].map(UF_NAME)
    if "Area_code" in df.columns:
        df["Area_label"] = df["Area_code"].map(AREA_MAP).fillna("NA")
    df["Sex_label"]  = df["Sex_code"].map(SEX_MAP).fillna("NA")
    df["Race_label"] = df["Race_code"].map(RACE_MAP).fillna("Unknown")
    df["School_label"] = df["School_code"].map(SCHOOL_MAP).fillna("NA")
    df["Occupation_label"] = df["Occupation_code"].map(OCC_MAP).fillna("NA")
    df["Contributor_label"] = df["Contributor_code"].map(CONTR_MAP).fillna("NA")

    return df

# ---------------------------
# 3) LOAD & CONCAT
# ---------------------------
frames = []
for f in INPUT_FILES:
    if not Path(f).exists():
        raise FileNotFoundError(f"File not found: {f}")
    frames.append(load_one_csv(f))

data = pd.concat(frames, ignore_index=True)

# ---------------------------
# 4) FILTER 14–25 (no aggregation)
# ---------------------------
data = data[(data["Age"] >= AGE_MIN) & (data["Age"] <= AGE_MAX)].copy()

# Optional sanity checks
assert (data["Age"] >= AGE_MIN).all() and (data["Age"] <= AGE_MAX).all()
print(f"Rows after age filter {AGE_MIN}-{AGE_MAX}: {len(data):,}")

# ---------------------------
# 5) SELECT/ORDER COLUMNS (raw codes + labels)
# ---------------------------
ordered_cols = [
    "Year","Quarter","id_uf","UF","UF_name",
    "Area_code","Area_label",
    "Sex_code","Sex_label",
    "Age",
    "Race_code","Race_label",
    "School_code","School_label",
    "Occupation_code","Occupation_label",
    "Contributor_code","Contributor_label",
    "Income_all_jobs","Weight_V1028"
]
data = data[[c for c in ordered_cols if c in data.columns]].reset_index(drop=True)


data.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
print(f"[OK] Saved: {OUTPUT_FILE}  | rows={len(data):,}")
print(data.head())