# 1. Import Libraries
import pandas as pd
import sidrapy

# -----------------------------------------------------------------------------
# 2. API Request
# -----------------------------------------------------------------------------
# This section constructs and executes the API call to IBGE's SIDRA database.
# We are using Table 6407 from the PNAD Contínua survey.
# Documentation for the sidrapy call: https://sidrapy.readthedocs.io/en/latest/
#
# Parameters explained:
# - table_code: 6407 - Population by study condition, occupation status, age, sex, and race.
# - period: '2022-2024' - Retrieves data for the last three available full years.
# - territorial_level: '1' (N1) - Brazil as a whole.
# - ibge_territorial_code: 'all' - To get the total for the national level.
# - variable: 8370 - Contingent of people (in thousands).
# - classifications:
#   - C1: Sex ('all' to get both Male and Female)
#   - C2: Color or Race ('all' to get all categories)
#   - C12401: Age groups. We select '15 to 17 years' (106346) and '18 to 24 years' (106347).
#   - C12402: Study condition. We select 'Not studying' (106350).
#   - C12403: Occupation status. We select 'Not occupied' (106352).

print("Fetching data from IBGE's SIDRA API... This may take a moment.")

# Construct the API request
data_raw = sidrapy.get_table(
    table_code="6407",
    period="2022-2024",
    territorial_level="1",
    ibge_territorial_code="all",
    variable="8370",
    classifications={
        "C1": "all",
        "C2": "all",
        "C12401": "106346,106347", # 15-17 years and 18-24 years
        "C12402": "106350",         # Condition: Not studying
        "C12403": "106352"          # Condition: Not occupied
    },
    header='n' # Use column names from the API response
)

print("Data fetched successfully.")

# -----------------------------------------------------------------------------
# 3. Initial Cleaning
# -----------------------------------------------------------------------------
# Convert the raw API response (a list of dictionaries) into a pandas DataFrame.
df = pd.DataFrame(data_raw)

# Select and rename essential columns for clarity
columns_to_keep = {
    'Ano': 'Ano',
    'Sexo': 'Sexo',
    'Cor ou raça': 'Cor ou raça',
    'Grupo de idade': 'Grupo de idade',
    'Condição de estudo': 'Condição de estudo',
    'Condição de ocupação': 'Condição de ocupação',
    'Valor': 'Valor'
}
df = df[columns_to_keep.keys()]

# The 'Valor' column may contain non-numeric characters ('-' or '...') for suppressed data.
# Convert 'Valor' to numeric, coercing errors into NaN (Not a Number).
# Then, fill any NaN values with 0, as they represent no recorded individuals.
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

# The API provides counts in thousands. We convert it to the absolute number.
df['Valor'] = df['Valor'] * 1000

# Convert the count to integer type for cleaner representation
df['Valor'] = df['Valor'].astype(int)

# -----------------------------------------------------------------------------
# 4. Filtering Data
# -----------------------------------------------------------------------------
# The API call has already performed the necessary filtering for the NEET population:
# - Age groups 15-17 and 18-24 years
# - Not studying
# - Not occupied
# No further filtering is needed here. The next step is to translate and aggregate.

# -----------------------------------------------------------------------------
# 5. Translation to English
# -----------------------------------------------------------------------------
# Create dictionaries to map Portuguese names and values to English.

# Dictionary for column names
column_translation = {
    'Ano': 'Year',
    'Sexo': 'Sex',
    'Cor ou raça': 'Race/Color',
    'Valor': 'NEET_Count'
}

# Dictionary for 'Sex' values
sex_translation = {
    'Homens': 'Male',
    'Mulheres': 'Female'
}

# Dictionary for 'Race/Color' values
race_translation = {
    'Branca': 'White',
    'Preta': 'Black',
    'Amarela': 'Asian',
    'Parda': 'Mixed-race',
    'Indígena': 'Indigenous',
    'Ignorado': 'Not specified' # Handle cases where race is not specified
}

# Apply translations
# First, translate the categorical values
df['Sexo'] = df['Sexo'].map(sex_translation)
df['Cor ou raça'] = df['Cor ou raça'].map(race_translation)

# Drop columns that are no longer needed after filtering and before aggregation
df = df[['Ano', 'Sexo', 'Cor ou raça', 'Valor']]

# -----------------------------------------------------------------------------
# 6. Final Aggregation
# -----------------------------------------------------------------------------
# Group data by Year, Sex, and Race/Color.
# Sum the 'Valor' to combine the counts from the two age groups (15-17 and 18-24)
# into a single total for the 15-24 age range.
df_final = df.groupby(['Ano', 'Sexo', 'Cor ou raça'])['Valor'].sum().reset_index()

# Translate the column names of the final aggregated DataFrame
df_final = df_final.rename(columns=column_translation)

# Sort the final dataframe for better presentation
df_final = df_final.sort_values(by=['Year', 'Sex', 'Race/Color']).reset_index(drop=True)

# -----------------------------------------------------------------------------
# 7. Display Output
# -----------------------------------------------------------------------------
print("\n--- Final Processed Data on NEET Youth (15-24 years) in Brazil ---")
print(df_final.head(15))
print("\n--- Data for the latest available year ---")
print(df_final[df_final['Year'] == df_final['Year'].max()])
