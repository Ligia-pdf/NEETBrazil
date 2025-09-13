# NEET Analysis in Brazil (PNAD Contínua)

## 📌 Project Overview
This project analyzes **NEET youth in Brazil** (Not in Employment, Education, or Training),  
with a particular focus on the **Northeast region**. The study is based on the PNAD Contínua microdata,  
accessed via the [Base dos Dados](https://basedosdados.org/) platform.

The main objectives are:
- Build a **raw dataset** from PNAD microdata (2023–2025).
- Organize and clean variables (sex, age, education, labor status, etc.).
- Define and identify the **NEET population** (15–24 years old).
- Explore key characteristics of NEET youth:
  - Gender distribution
  - Age groups
  - Educational attainment
  - Regional focus (Northeast)
  - Additional sociodemographic variables

---

## 🗂 Data Source
- **PNAD Contínua (IBGE)**  
- Downloaded through **basedosdados** with SQL queries on Google BigQuery.  
- Years covered: **2023, 2024, and 2025 (Q1)**.  

---

## ⚙️ Methodology
1. **Data Extraction**  
   - SQL query selects relevant PNAD variables.  
   - Saved as `dados_brutos.csv`.  

2. **Data Cleaning**  
   - Convert raw codes into interpretable labels.  
   - Example: `sex_code` → `female` (1 = Female, 0 = Male).  
   - Drop unused variables (e.g., `children_under14_code`).  

3. **Filtering Scope**  
   - Focus on **Q1 2025**.  
   - Age filter: **15–24 years old**.  

4. **NEET Definition**  
   - Not in school (`school_code = 2`).  
   - Not employed (`occupation_code != 1` OR `labor_force_code = 2`).  
