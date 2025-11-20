import streamlit as st
import pandas as pd
import io
import sys
import os

# Add project root to path to allow importing dcapt modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dcapt.constants import (
    TN_DEPARTMENTS, TN_SCHEMES_MAP, ALL_SCHEMES, TN_DISTRICTS,
    HAZARDS, SEVERITY_OPTIONS, TECH_COMPLEXITY_OPTIONS, 
    QUALITATIVE_MAP, CO_BENEFITS_MAP
)

# --- Page Config ---
st.set_page_config(page_title="DCAPT Tamil Nadu", layout="wide")

# --- Helper Functions ---
def get_score(value):
    return QUALITATIVE_MAP.get(value, 0.0)

def calculate_priority(data):
    # 1. Hazard Component
    hazard_score = get_score(data['Hazard_Severity'])
    
    # 2. Capacity Component (Avg of Tech + Infra)
    tech_score = get_score(data['Technical_Complexity'])
    infra_score = get_score(data['Infrastructure_Maturity'])
    capacity_score = (tech_score + infra_score) / 2
    
    # 3. Co-Benefit Component (SUMS)
    raw_cb_sum = (
        data['Social_Benefit_Score'] + 
        data['Economic_Benefit_Score'] + 
        data['Environmental_Benefit_Score'] + 
        data['Mitigation_Benefit_Score']
    )
    
    # Normalize Co-Benefits
    total_items = sum(len(v) for v in CO_BENEFITS_MAP.values()) 
    max_possible = total_items * 10 
    cb_component_score = (raw_cb_sum / max_possible) * 10
    
    # 4. Convergence Component
    conv_score = get_score(data['Scheme_Alignment'])
    
    # Final Equal Weight Score
    final_score = (hazard_score + capacity_score + cb_component_score + conv_score) / 4
    
    return final_score, raw_cb_sum, cb_component_score

# --- Sidebar: Intervention List ---
if 'interventions' not in st.session_state:
    st.session_state.interventions = []

st.sidebar.title("DCAPT Actions")
with st.sidebar.expander("📋 Saved Interventions", expanded=True):
    if st.session_state.interventions:
        df_saved = pd.DataFrame(st.session_state.interventions)
        st.dataframe(df_saved[['Intervention_Name', 'Priority_Score']], hide_index=True)
        
        # Download Button
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_saved.to_excel(writer, sheet_name='Interventions', index=False)
        
        st.download_button(
            label="📥 Download Excel",
            data=buffer,
            file_name="dcapt_prioritized_list.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.info("No interventions added yet.")

# --- Main Form ---
st.title("🌴 DCAPT: District Climate Action Planning Tool")
st.markdown("### Tamil Nadu District Edition")

# --- Location Context (New) ---
st.markdown("#### 📍 Location Context")
lc1, lc2 = st.columns(2)
with lc1:
    state = st.selectbox("State", ["Tamil Nadu"])
with lc2:
    district = st.selectbox("District", TN_DISTRICTS)

# Climate Profile Pop-up (Placeholder)
with st.expander(f"🌍 View Climate Profile: {district}", expanded=False):
    st.info(f"Climate Hazard Profile for **{district}**")
    st.markdown("""
    **Projected Hazards (2030):**
    - 🌊 **Flood Risk**: High (Coastal/Riverine)
    - ☀️ **Heatwave**: Medium
    - 🌀 **Cyclone**: High
    
    *(Map Visualization Placeholder)*
    """)
    st.caption("Note: This data will be auto-populated from climate projections in future updates.")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Context & Hazard")
    primary_hazard = st.selectbox("Primary Hazard", HAZARDS)
    hazard_severity = st.select_slider("Hazard Severity (Local Context)", options=SEVERITY_OPTIONS, value="High")
    
    st.subheader("2. Intervention Details")
    int_name = st.text_input("Intervention Name", placeholder="e.g., Construction of Check Dam at Village X")
    sector = st.selectbox("Sector", ["Water", "Agriculture", "Livestock", "Forestry", "Urban", "Health"])
    
    st.subheader("3. Department & Finance")
    anchor_dept = st.selectbox("Anchor Department", TN_DEPARTMENTS)
    
    # Dynamic Scheme Filtering
    available_schemes = TN_SCHEMES_MAP.get(anchor_dept, ALL_SCHEMES)
    finance_source = st.selectbox("Source of Finance (Scheme)", available_schemes)
    
    collab_depts = st.multiselect("Collaborating Departments", TN_DEPARTMENTS)

with col2:
    st.subheader("4. Feasibility & Capacity")
    tech_complexity = st.selectbox("Technical Complexity", TECH_COMPLEXITY_OPTIONS)
    infra_maturity = st.select_slider("Infrastructure Maturity", options=SEVERITY_OPTIONS, value="Medium")
    
    st.subheader("5. Convergence")
    scheme_alignment = st.select_slider("Scheme Alignment Score", options=SEVERITY_OPTIONS, value="High")

# --- Co-Benefits Calculator (Full Width) ---
st.divider()
st.subheader("6. Co-Benefits Calculator")
st.info("Select applicable benefits and rate their impact (1-10). Scores are SUMMED.")

cb_cols = st.columns(4)
categories = ["Social", "Economic", "Environmental", "Mitigation"]
category_scores = {}

for i, cat in enumerate(categories):
    with cb_cols[i]:
        st.markdown(f"**{cat} Benefits**")
        benefits = CO_BENEFITS_MAP.get(cat, [])
        
        total_cat_score = 0
        
        for ben in benefits:
            chk_key = f"chk_{cat}_{ben}"
            slider_key = f"sl_{cat}_{ben}"
            
            is_checked = st.checkbox(ben, key=chk_key)
            if is_checked:
                val = st.slider(f"Impact", 1, 10, 5, key=slider_key, label_visibility="collapsed")
                total_cat_score += val
        
        category_scores[f"{cat}_Benefit_Score"] = total_cat_score
        st.metric(f"{cat} Sum", f"{total_cat_score}")

# --- Real-time Scoring ---
current_data = {
    'Hazard_Severity': hazard_severity,
    'Technical_Complexity': tech_complexity,
    'Infrastructure_Maturity': infra_maturity,
    'Scheme_Alignment': scheme_alignment,
    **category_scores 
}

final_score, raw_cb_sum, norm_cb_score = calculate_priority(current_data)

st.divider()
st.markdown("### 🎯 Priority Score Preview")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Co-Benefit Sum", f"{raw_cb_sum}")
with c2:
    st.metric("Normalized Co-Benefit (0-10)", f"{norm_cb_score:.1f}")
with c3:
    score_color = "green" if final_score >= 7.5 else "orange" if final_score >= 5 else "red"
    st.markdown(f"<h1 style='text-align: center; color: {score_color};'>{final_score:.2f} / 10</h1>", unsafe_allow_html=True)

# Add Button
if st.button("➕ Add Intervention to List", type="primary"):
    if int_name:
        new_entry = {
            "Intervention_Name": int_name,
            "District": district, # Added District
            "Sector": sector,
            "Primary_Hazard": primary_hazard,
            "Anchor_Dept": anchor_dept,
            "Finance_Source": finance_source,
            "Priority_Score": round(final_score, 2),
            "CoBenefit_Sum": raw_cb_sum,
            **current_data 
        }
        st.session_state.interventions.append(new_entry)
        st.success(f"Added '{int_name}'!")
        st.rerun()
    else:
        st.error("Please enter an Intervention Name.")
