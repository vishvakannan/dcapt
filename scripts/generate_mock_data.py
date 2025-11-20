import pandas as pd
import numpy as np
import random
import os

# Define the output path
OUTPUT_FILE = "mock_dcapt_data.csv"

def generate_mock_data(num_rows=100):
    """
    Generates a synthetic dataset for DCAPT prioritization.
    """
    data = []
    
    for i in range(num_rows):
        # Randomly pick qualitative values
        hazard = random.choice(["Very High", "High", "Medium", "Low", "Very Low"])
        finance = random.choice(["High", "Medium", "Low"])
        tech = random.choice(["High", "Medium", "Low"])
        co_benefits = random.choice(["High", "Medium", "Low"])
        
        # Generate a synthetic "Expert Score" based on a hidden logic (ground truth)
        # Logic: Hazard * 0.4 + Finance * 0.2 + Tech * 0.2 + CoBenefits * 0.2
        # We map them to numbers first to calculate the score
        h_val = {"Very High": 10, "High": 8, "Medium": 5, "Low": 2, "Very Low": 0}[hazard]
        f_val = {"High": 10, "Medium": 5, "Low": 2}[finance]
        t_val = {"High": 10, "Medium": 5, "Low": 2}[tech]
        c_val = {"High": 10, "Medium": 5, "Low": 2}[co_benefits]
        
        # Add some noise to simulate human inconsistency
        noise = np.random.normal(0, 1.0)
        
        score = (h_val * 0.4) + (f_val * 0.2) + (t_val * 0.2) + (c_val * 0.2) + noise
        score = max(0, min(10, score)) # Clip between 0 and 10
        
        data.append({
            "Intervention_ID": f"INT_{i:03d}",
            "Hazard_Score": hazard,
            "Finance_Capacity": finance,
            "Tech_Capacity": tech,
            "Co_Benefits": co_benefits,
            "Expert_Score": round(score, 2)
        })
        
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Generated {num_rows} rows of mock data at {OUTPUT_FILE}")
    return df

if __name__ == "__main__":
    generate_mock_data()
