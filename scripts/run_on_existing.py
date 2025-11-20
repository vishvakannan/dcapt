import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from dcapt.data_processor import load_and_process_data

INPUT_FILE = "dcapt.xlsx"
OUTPUT_FILE = "dcapt_mapped_output.xlsx"

def run_mapping():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    print(f"Processing {INPUT_FILE} with new schema logic...")
    try:
        df = load_and_process_data(INPUT_FILE)
        
        # Select relevant columns to show mapping success
        cols_to_show = [
            "Intervention_Name", 
            "Composite_Hazard_Score", 
            "Financial_Capacity_Score", 
            "Equal_Weight_Score"
        ]
        # Add any new columns that might be interesting if they are not 0
        
        print("\nMapping Successful. First 5 rows of calculated scores:")
        print(df[cols_to_show].head())
        
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\nFull mapped data saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_mapping()
