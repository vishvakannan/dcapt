import pandas as pd
from dcapt.data_processor import get_template_dataframe

def generate_template():
    df = get_template_dataframe()
    
    # Add one example row
    example_row = {
        "Intervention_ID": "INT_001",
        "Intervention_Name": "Example: Check Dam Construction",
        "Sector": "Water",
        "Drought_Risk_Score": 8.0,
        "Flood_Risk_Score": 2.0,
        "Financial_Capacity_Score": 7.0,
        "Current_Technical_Capacity": 6.0,
        "Social_Benefit_Score": 9.0,
        "Estimated_Cost_INR": 500000,
        "Scheme_Count": 2
    }
    df = pd.concat([df, pd.DataFrame([example_row])], ignore_index=True)
    
    output_path = "dcapt_new_template.xlsx"
    df.to_excel(output_path, index=False)
    print(f"Template generated at: {output_path}")

if __name__ == "__main__":
    generate_template()
