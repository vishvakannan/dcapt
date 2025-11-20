import pandas as pd
import xlsxwriter

OUTPUT_FILE = "dcapt_tn_template.xlsx"

# --- Data Lists ---
TN_DEPARTMENTS = [
    "Rural Development & Panchayat Raj",
    "Agriculture & Farmers Welfare",
    "Water Resources Department (WRD)",
    "Environment, Climate Change & Forests",
    "Municipal Administration & Water Supply (MAWS)",
    "Housing & Urban Development",
    "Animal Husbandry, Dairying & Fisheries",
    "Energy Department",
    "Highways & Minor Ports",
    "Social Welfare & Women Empowerment"
]

TN_SCHEMES = [
    "MGNREGS (RD&PR)",
    "PMKSY (Agri)",
    "Jal Jeevan Mission (MAWS)",
    "Green Tamil Nadu Mission (Forest)",
    "Namakku Naame Thittam",
    "Kalaignar All Village Integrated Agri Dev",
    "NABARD RIDF",
    "State Balanced Growth Fund",
    "Generic Scheme 1A",
    "Generic Scheme 1B",
    "Grant 1"
]

HAZARDS = ["Flood", "Drought", "Heatwave", "Cyclone", "Sea Level Rise", "Salinity Ingress"]
SEVERITY = ["Very High", "High", "Medium", "Low"]
TECH_COMPLEXITY = [
    "Easy - NREGA/In-house",
    "Medium - Tech Support Needed",
    "Hard - Outsourcing Required"
]
ALIGNMENT = ["Very High", "High", "Medium", "Low"]

# --- Column Definitions ---
COLUMNS = [
    {"header": "Intervention_ID", "width": 15, "type": "text"},
    {"header": "Primary_Hazard", "width": 20, "type": "list", "options": HAZARDS},
    {"header": "Hazard_Severity", "width": 15, "type": "list", "options": SEVERITY, "note": "Severity in local context"},
    {"header": "Intervention_Name", "width": 40, "type": "text"},
    {"header": "Anchor_Department", "width": 30, "type": "list", "options": TN_DEPARTMENTS},
    {"header": "Collaborating_Departments", "width": 30, "type": "list", "options": TN_DEPARTMENTS, "note": "Select primary collaborator"},
    
    # Finance & Tech
    {"header": "Source_of_Finance", "width": 25, "type": "list", "options": TN_SCHEMES},
    {"header": "Technical_Complexity", "width": 25, "type": "list", "options": TECH_COMPLEXITY},
    {"header": "Infrastructure_Maturity", "width": 20, "type": "list", "options": SEVERITY},
    
    # Co-Benefits (Users should use the sub-tool to fill these)
    {"header": "Social_Benefit_Score", "width": 18, "type": "list", "options": SEVERITY, "note": "Use Co-Benefits Sheet"},
    {"header": "Economic_Benefit_Score", "width": 18, "type": "list", "options": SEVERITY, "note": "Use Co-Benefits Sheet"},
    {"header": "Env_Benefit_Score", "width": 18, "type": "list", "options": SEVERITY, "note": "Use Co-Benefits Sheet"},
    {"header": "Mitigation_Potential", "width": 18, "type": "list", "options": SEVERITY, "note": "Use Co-Benefits Sheet"},
    
    # Convergence
    {"header": "Scheme_Names", "width": 30, "type": "text", "note": "Comma separated"},
    {"header": "Scheme_Alignment_Score", "width": 20, "type": "list", "options": ALIGNMENT},
    {"header": "Estimated_Cost_INR", "width": 15, "type": "number"},
    {"header": "Dept_Priority_Rank", "width": 15, "type": "number"},
]

def generate_tn_template():
    workbook = xlsxwriter.Workbook(OUTPUT_FILE)
    
    # --- Sheet 1: Interventions ---
    ws_main = workbook.add_worksheet("Interventions")
    
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})
    
    for i, col in enumerate(COLUMNS):
        ws_main.write(0, i, col["header"], header_format)
        ws_main.set_column(i, i, col["width"])
        
        if col.get("type") == "list":
            ws_main.data_validation(1, i, 1000, i, {'validate': 'list', 'source': col["options"]})
        
        if col.get("note"):
            ws_main.write_comment(0, i, col["note"])

    # --- Sheet 2: Co-Benefits Calculator ---
    ws_cob = workbook.add_worksheet("Co-Benefits Calculator")
    ws_cob.write(0, 0, "Co-Benefit Identification Tool", workbook.add_format({'bold': True, 'font_size': 14}))
    ws_cob.write(1, 0, "Identify benefits for a specific intervention and estimate the score.")
    
    # Simple Checklist Structure
    headers = ["Benefit Category", "Specific Benefit", "Applies? (Yes/No)", "Impact Level (1-10)"]
    for i, h in enumerate(headers):
        ws_cob.write(3, i, h, header_format)
        ws_cob.set_column(i, i, 25)
        
    benefits = [
        ("Social", "Improves Public Health"),
        ("Social", "Generates Employment (NREGA)"),
        ("Social", "Empowers Women/SHGs"),
        ("Economic", "Increases Crop Yield"),
        ("Economic", "Protects Assets from Damage"),
        ("Environmental", "Sequesters Carbon"),
        ("Environmental", "Recharges Groundwater"),
        ("Environmental", "Enhances Biodiversity"),
    ]
    
    for row, (cat, ben) in enumerate(benefits, start=4):
        ws_cob.write(row, 0, cat)
        ws_cob.write(row, 1, ben)
        ws_cob.data_validation(row, 2, row, 2, {'validate': 'list', 'source': ["Yes", "No"]})
        ws_cob.data_validation(row, 3, row, 3, {'validate': 'integer', 'criteria': 'between', 'minimum': 1, 'maximum': 10})

    # --- Sheet 3: Instructions ---
    ws_intro = workbook.add_worksheet("Instructions")
    ws_intro.write(0, 0, "DCAPT Tamil Nadu - User Guide", workbook.add_format({'bold': True, 'font_size': 14}))
    ws_intro.write(2, 0, "1. Start with 'Interventions' sheet.")
    ws_intro.write(3, 0, "2. Select the Primary Hazard (e.g., Drought).")
    ws_intro.write(4, 0, "3. Choose the Anchor Department from the TN Dept list.")
    ws_intro.write(5, 0, "4. Use the 'Co-Benefits Calculator' sheet to help estimate the benefit scores.")
    
    workbook.close()
    print(f"TN Template generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_tn_template()
