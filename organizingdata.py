import pandas as pd

# 1) read
df = pd.read_csv("dados_brutos_2023_2024.csv")

# 2) oficial dictionaries
uf_map = {
    11:'RO',12:'AC',13:'AM',14:'RR',15:'PA',16:'AP',17:'TO',21:'MA',22:'PI',
    23:'CE',24:'RN',25:'PB',26:'PE',27:'AL',28:'SE',29:'BA',31:'MG',32:'ES',
    33:'RJ',35:'SP',41:'PR',42:'SC',43:'RS',50:'MS',51:'MT',52:'GO',53:'DF'
}

area_map = {1:'Urban', 2:'Rural'}  # V1022
sex_map = {1:'Male', 2:'Female'}   # V2007

race_map = {
    1:'White', 2:'Black', 3:'Yellow(Asian)', 4:'Brown(Mixed-race)',
    5:'Indigenous', 9:'Ignored'
}  # V2010

school_map = {1:'Yes', 2:'No'}  # V3002

# VD4002: somente ocupado/desocupado
occupation_map = {1:'Employed', 2:'Unemployed'}  # VD4002

# VD3004: nível de instrução (sistema 9 anos) – 1..7
education_map = {
    1:'No schooling / <1 year',
    2:'Incomplete Elementary',
    3:'Complete Elementary',
    4:'Incomplete High School',
    5:'Complete High School',
    6:'Incomplete Higher Education',
    7:'Complete Higher Education'
}

# VD4005: desalento (1 = desalentado). Vamos rotular como Yes/No, mantendo NA se vier vazio.
def map_desalento(x):
    if pd.isna(x): 
        return pd.NA
    try:
        return 'Discouraged (desalentado): Yes' if int(x) == 1 else 'Discouraged (desalentado): No'
    except:
        return pd.NA

# 3) Aplicar mapeamentos sem perder os originais (opcional: preserve cols com sufixo _code)
out = df.copy()
out['uf'] = out['id_uf'].map(uf_map)
out['area'] = out['area_code'].map(area_map)
out['sex'] = out['sex_code'].map(sex_map)
out['race'] = out['race_code'].map(race_map)
out['in_school'] = out['school_code'].map(school_map)
out['occupation_status'] = out['occupation_code'].map(occupation_map)
out['education_level'] = out['education_code'].map(education_map)
out['discouraged_flag'] = out['reason_code'].apply(map_desalento)

# 4) Ordenar colunas de forma “humana”
cols_order = [
    'ano','trimestre','id_uf','uf','area','sex','age','race',
    'in_school','occupation_status','education_level','discouraged_flag','weight'
]
# Garante que só usa colunas existentes
cols_order = [c for c in cols_order if c in out.columns]
out = out[cols_order]

# 5) save
out.to_csv("dados_rotulados.csv", index=False)
print("OK! Arquivo salvo como dados_rotulados.csv")
