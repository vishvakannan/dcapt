import pandas as pd
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from dcapt.data_processor import load_and_process_data

TEMPLATE_FILE = "dcapt_tn_template.xlsx"
TEST_FILE = "dcapt_tn_test_filled.xlsx"

def test_tn_template_processing():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: {TEMPLATE_FILE} not found.")
        return

    print(f"Loading template {TEMPLATE_FILE}...")
    # Load the template to get columns
    df = pd.read_excel(TEMPLATE_FILE, sheet_name="Interventions")
    
    # Create a dummy row with TN specific values
    dummy_row = {
        "Intervention_ID": "TEST_001",
        "Primary_Hazard": "Drought",
        "Hazard_Severity": "High", # Should map to 8.0
        "Intervention_Name": "Test Pond",
        "Anchor_Department": "Rural Development & Panchayat Raj",
        "Source_of_Finance": "MGNREGS (RD&PR)",
        "Technical_Complexity": "Easy - NREGA/In-house", # Should map to 10.0
        "Infrastructure_Maturity": "Medium", # Should map to 5.0
        "Social_Benefit_Score": "High", # 8.0
        "Economic_Benefit_Score": "Medium", # 5.0
        "Env_Benefit_Score": "Very High", # 10.0
        "Mitigation_Potential": "Low", # 2.0
        "Scheme_Names": "MGNREGS",
        "Scheme_Alignment_Score": "High" # 8.0
    }
    
    # Append dummy row
    df_filled = pd.concat([df, pd.DataFrame([dummy_row])], ignore_index=True)
    df_filled.to_excel(TEST_FILE, sheet_name="Interventions", index=False)
    print(f"Created filled test file: {TEST_FILE}")
    
    # Run Processor
    print("Running Data Processor...")
    try:
        processed_df = load_and_process_data(TEST_FILE)
        
        # Check Scores
        row = processed_df.iloc[0]
        print("\n--- Processing Results ---")
        print(f"Primary Hazard: {row['Primary_Hazard']}")
        print(f"Hazard Severity (Input: High): {row['Hazard_Severity']} (Expected: 8.0)")
        print(f"Tech Complexity (Input: Easy): {row['Technical_Complexity_Score']} (Expected: 10.0)")
        print(f"Equal Weight Score: {row['Equal_Weight_Score']:.2f}")
        
        # Validation
        assert row['Hazard_Severity'] == 8.0
        assert row['Technical_Complexity_Score'] == 10.0
        print("\nSUCCESS: Data Processor correctly handled TN Template inputs!")
        
    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tn_template_processing()
