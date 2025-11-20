# DCAPT Constants

# --- TN Data Lists ---
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

TN_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", "Dindigul", 
    "Erode", "Kallakurichi", "Kancheepuram", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai", 
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", 
    "Ranipet", "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi", 
    "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", 
    "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar"
]

# Map Departments to specific schemes for dynamic filtering
TN_SCHEMES_MAP = {
    "Rural Development & Panchayat Raj": ["MGNREGS", "PMAY-G", "RGSA", "State Finance Commission Grants"],
    "Agriculture & Farmers Welfare": ["PMKSY", "NMSA", "Kalaignar All Village Integrated Agri Dev", "Crop Insurance"],
    "Water Resources Department (WRD)": ["IAMWARM", "Dam Rehabilitation (DRIP)", "Nadanthai Vaazhi Cauvery"],
    "Environment, Climate Change & Forests": ["Green Tamil Nadu Mission", "Wetland Mission", "Climate Change Mission"],
    "Municipal Administration & Water Supply (MAWS)": ["Jal Jeevan Mission", "AMRUT", "Smart Cities Mission", "Namakku Naame"],
    "Housing & Urban Development": ["Housing for All", "Urban Livelihood Mission"],
    "Animal Husbandry, Dairying & Fisheries": ["Kisan Credit Card (AH)", "Livestock Insurance", "Blue Revolution"],
    "Energy Department": ["PM-KUSUM (Solar)", "Rooftop Solar Scheme"],
    "Highways & Minor Ports": ["CRIDP", "Road Safety Fund"],
    "Social Welfare & Women Empowerment": ["Marriage Assistance Schemes", "Girl Child Protection"]
}

# Fallback list
ALL_SCHEMES = [s for schemes in TN_SCHEMES_MAP.values() for s in schemes] + ["Generic Grant", "CSR Funds", "District Mineral Fund"]

HAZARDS = ["Flood", "Drought", "Heatwave", "Cyclone", "Sea Level Rise", "Salinity Ingress"]

# Inverted Options (Low -> High) for Sliders
SEVERITY_OPTIONS = ["None", "Very Low", "Low", "Medium", "High", "Very High"]
ALIGNMENT_OPTIONS = ["Low", "Medium", "High", "Very High"]

TECH_COMPLEXITY_OPTIONS = [
    "Easy - NREGA/In-house",
    "Medium - Tech Support Needed",
    "Hard - Outsourcing Required"
]

# --- Co-Benefits Checklist ---
CO_BENEFITS_MAP = {
    "Social": [
        "Improves Public Health (e.g., vector control, sanitation)",
        "Generates Employment (e.g., NREGA person-days)",
        "Empowers Women/SHGs",
        "Enhances Food Security"
    ],
    "Economic": [
        "Increases Crop Yield / Productivity",
        "Protects Assets from Damage (Flood/Cyclone)",
        "Diversifies Income Sources",
        "Reduces Maintenance Costs"
    ],
    "Environmental": [
        "Recharges Groundwater",
        "Enhances Biodiversity / Green Cover",
        "Improves Soil Health",
        "Reduces Pollution (Air/Water)"
    ],
    "Mitigation": [
        "Sequesters Carbon (e.g., plantation)",
        "Reduces GHG Emissions (e.g., solar, efficiency)",
        "Promotes Renewable Energy"
    ]
}

# --- Scoring Logic ---
QUALITATIVE_MAP = {
    "Very High": 10.0,
    "High": 8.0,
    "Medium": 5.0,
    "Low": 2.0,
    "Very Low": 0.0,
    "None": 0.0,
    
    # Tech Complexity
    "Easy - NREGA/In-house": 10.0,
    "Medium - Tech Support Needed": 5.0,
    "Hard - Outsourcing Required": 2.0,
}
