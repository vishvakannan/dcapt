import pandas as pd
import numpy as np

# --- New TN District Schema Definition ---
SCHEMA_MAPPING = {
    # Core
    "Intervention Code": "Intervention_ID",
    "Intervention": "Intervention_Name",
    "Sector": "Sector",
    
    # Context
    "Anchor department": "Anchor_Department",
    "Collaborating departments": "Collaborating_Departments",
    "Schemes": "Scheme_Names",
    "Dept Prioritisation rank": "Dept_Priority_Rank",
    
    # New User Workflow
    "Primary Hazard": "Primary_Hazard",
    "Hazard Severity": "Hazard_Severity", # User selects High/Med/Low for the specific context
    "Source of Finance": "Source_of_Finance",
    "Technical Complexity": "Technical_Complexity",
    
    # Co-Benefits (Aggregated from sub-tool)
    "Social Benefits Score": "Social_Benefit_Score",
    "Economic Benefits Score": "Economic_Benefit_Score",
    "Environmental Benefits Score": "Env_Benefit_Score",
    "Mitigation Potential": "Mitigation_Potential",
}

# Mapping logic for Qualitative Inputs
QUALITATIVE_MAP = {
    # General Scale
    "Very High": 10.0,
    "High": 8.0,
    "Medium": 5.0,
    "Low": 2.0,
    "Very Low": 0.0,
    "None": 0.0,
    
    # Technical Complexity (Easy is Better/Higher Priority)
    "Easy - NREGA/In-house": 10.0,
    "Medium - Tech Support Needed": 5.0,
    "Hard - Outsourcing Required": 2.0,
}

NEW_COLUMNS = [
    "Primary_Hazard",
    "Hazard_Severity",
    "Source_of_Finance",
    "Technical_Complexity",
    "Infrastructure_Maturity",
    "Collaboration_Complexity",
    "Scheme_Alignment_Score",
    "Estimated_Cost_INR",
    "Scheme_Count"
]

def load_and_process_data(filepath: str) -> pd.DataFrame:
    """
    Loads data, maps to new TN schema, converts text to numbers, and calculates priority.
    """
    try:
        if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
            # Read 'Interventions' sheet if it exists, else first sheet
            xls = pd.ExcelFile(filepath)
            if 'Interventions' in xls.sheet_names:
                df = pd.read_excel(filepath, sheet_name='Interventions')
            else:
                df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

    # 1. Rename existing columns
    df_renamed = df.rename(columns=SCHEMA_MAPPING)
    
    # 2. Add missing new columns with default
    for col in NEW_COLUMNS:
        if col not in df_renamed.columns:
            df_renamed[col] = 0.0

    # 3. Convert Qualitative Text to Numbers
    # Special handling for Technical Complexity
    if "Technical_Complexity" in df_renamed.columns:
        df_renamed["Technical_Complexity_Score"] = df_renamed["Technical_Complexity"].map(QUALITATIVE_MAP).fillna(0.0)
    
    # General handling for others
    for col in ["Hazard_Severity", "Infrastructure_Maturity", "Scheme_Alignment_Score", 
                "Social_Benefit_Score", "Economic_Benefit_Score", "Env_Benefit_Score", "Mitigation_Potential"]:
        if col in df_renamed.columns:
            if df_renamed[col].dtype == 'O':
                df_renamed[col] = df_renamed[col].map(QUALITATIVE_MAP).fillna(0.0)
            else:
                df_renamed[col] = pd.to_numeric(df_renamed[col], errors='coerce').fillna(0.0)

    # 4. Derived Columns
    if "Scheme_Names" in df_renamed.columns:
        df_renamed['Scheme_Count'] = df_renamed['Scheme_Names'].astype(str).apply(
            lambda x: len(x.split(',')) if x.lower() != 'nan' and x.strip() != '' else 0
        )

    # 5. Calculate Equal Weight Score
    
    # Component: Hazard
    # Use Hazard Severity directly (User defines severity of the Primary Hazard)
    df_renamed['Hazard_Component'] = df_renamed['Hazard_Severity']
        
    # Component: Capacity
    # Avg of (Technical Complexity Score + Infrastructure Maturity)
    # Note: Source of Finance is now a label, not a score. We assume if Source exists, it's good?
    # Let's add a "Finance Score" based on whether Source is filled? 
    # For now, let's just use Tech + Infra.
    cap_cols = ["Technical_Complexity_Score", "Infrastructure_Maturity"]
    df_renamed['Capacity_Component'] = df_renamed[cap_cols].mean(axis=1)
    
    # Component: Co-Benefits (Avg)
    ben_cols = ["Social_Benefit_Score", "Economic_Benefit_Score", "Env_Benefit_Score", "Mitigation_Potential"]
    df_renamed['CoBenefit_Component'] = df_renamed[ben_cols].mean(axis=1)
    
    # Component: Convergence
    df_renamed['Convergence_Component'] = df_renamed['Scheme_Alignment_Score']
    mask_no_align = df_renamed['Convergence_Component'] == 0
    df_renamed.loc[mask_no_align, 'Convergence_Component'] = (df_renamed.loc[mask_no_align, 'Scheme_Count'] * 2).clip(upper=10)

    # Final Score
    df_renamed['Equal_Weight_Score'] = (
        df_renamed['Hazard_Component'] + 
        df_renamed['Capacity_Component'] + 
        df_renamed['CoBenefit_Component'] + 
        df_renamed['Convergence_Component']
    ) / 4

    return df_renamed
