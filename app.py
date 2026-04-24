import streamlit as st
import pandas as pd
import os
import sys
from PIL import Image

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from pipeline import CDSSPipeline
import eda_visualizations as ev

# --- Page Configuration ---
st.set_page_config(
    page_title="NEUROCARE | Professional CDSS",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme Management ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

# --- Premium Professional Styling ---
def get_custom_css(theme):
    if theme == 'Light':
        bg = "#F8FAFC"
        card_bg = "#FFFFFF"
        text = "#0F172A"
        border = "#E2E8F0"
        accent = "#0284C7"
        sidebar_bg = "#FFFFFF"
    else:
        bg = "#111827"
        card_bg = "#1F2937"
        text = "#F1F5F9"
        border = "#374151"
        accent = "#38BDF8"
        sidebar_bg = "#111827"

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"], .stMarkdown, .stText, .stCaption {{
            font-family: 'Inter', sans-serif;
            color: {text} !important;
        }}
        
        .stApp {{
            background-color: {bg} !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {border};
        }}

        /* Clean Headers */
        h1, h2, h3 {{
            color: {text} !important;
            font-weight: 700 !important;
            letter-spacing: -0.025em;
        }}
        
        /* Modern Cards */
        .professional-card {{
            background-color: {card_bg};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        }}

        .diagnostic-header {{
            background-color: {accent};
            color: white !important;
            padding: 2.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }}

        .stButton>button {{
            background-color: {accent} !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.2rem !important;
        }}

        .status-badge {{
            padding: 0.4rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
        }}
        .severity-high {{ background-color: #EF4444; color: white !important; }}
        .severity-mod {{ background-color: #F59E0B; color: white !important; }}
        .severity-low {{ background-color: #10B981; color: white !important; }}
    </style>
    """

st.markdown(get_custom_css(st.session_state.theme), unsafe_allow_html=True)

# --- Initialization ---
@st.cache_resource(ttl=3600)
def get_cdss_pipeline_v3():
    DATA_DIR = os.path.join(os.getcwd(), 'data')
    MODEL_PATH = os.path.join(os.getcwd(), 'src', 'risk_model.json')
    pipeline = CDSSPipeline(DATA_DIR, MODEL_PATH)
    pipeline.initialize()
    return pipeline

try:
    pipeline = get_cdss_pipeline_v3()
except Exception as e:
    st.error(f"System Offline: {e}")

# --- Navigation ---
with st.sidebar:
    st.markdown("### NEUROCARE")
    st.session_state.theme = st.selectbox("Interface Theme", ["Light", "Dark"])
    st.divider()
    mode = st.radio("Strategic Workspace", ["Population Insights", "Clinical Consultation", "Registry Patient Search"])
    st.divider()
    st.caption("Engine: CDSS-Pro v3.2")
    st.caption("Environment: Interactive Analytical Mode")

# --- Interactive Colors for Plotly ---
TH_COLORS = {
    'primary': "#0F172A" if st.session_state.theme == "Light" else "#F1F5F9",
    'secondary': "#0284C7",
    'accent': "#0EA5E9"
}

# --- Workspace Logic ---
if mode == "Population Insights":
    st.markdown("<div class='diagnostic-header'><h1>Population Health Strategic Insights</h1><p>Real-time analytical trends across the active patient registry.</p></div>", unsafe_allow_html=True)
    
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        st.plotly_chart(ev.plot_age_distribution(pipeline.datasets['patients'], TH_COLORS), use_container_width=True)
    with row1_c2:
        st.plotly_chart(ev.plot_gender_breakdown(pipeline.datasets['patients'], TH_COLORS), use_container_width=True)
        
    st.divider()
    row2_c1, row2_c2 = st.columns([1.5, 1])
    with row2_c1:
        st.plotly_chart(ev.plot_top_conditions(pipeline.datasets['conditions'], TH_COLORS), use_container_width=True)
    with row2_c2:
        st.plotly_chart(ev.plot_expense_analysis(pipeline.datasets['patients'], TH_COLORS), use_container_width=True)

elif mode == "Registry Patient Search":
    st.markdown("<div class='diagnostic-header'><h1>Patient Registry Search</h1><p>Retrieve and analyze historic Electronic Health Records.</p></div>", unsafe_allow_html=True)
    
    patient_list = pipeline.features_df.index.tolist()
    patient_id = st.selectbox("Search Medical ID", [""] + patient_list)
    
    if patient_id:
        with st.spinner("Analyzing Medical History..."):
            report = pipeline.analyze_from_db(patient_id)
            
        col_prof, col_desc = st.columns([1, 2])
        with col_prof:
            st.markdown(f"### {report['patient_name']}")
            st.markdown(f"**Clinical Severity:** <span class='status-badge severity-{report['severity'].lower()[:3]}'>{report['severity']}</span>", unsafe_allow_html=True)
            st.metric("Hospitalization Risk", f"{report['ai_risk_score'] * 100:.1f}%")
        
        with col_desc:
            st.markdown("#### Clinical Case Summary")
            st.write(report['summary'])
            
        st.divider()
        a_c, r_c, v_c = st.columns([1,1,1])
        with a_c:
            st.markdown("#### Active Clinical Alerts")
            for a in report['alerts']: st.error(a)
        with r_c:
            st.markdown("#### Prescriptive Guidance")
            for r in report['recommendations']: st.success(r)
        with v_c:
            st.plotly_chart(ev.plot_individual_vitals(report['vitals_summary'], TH_COLORS), use_container_width=True)

elif mode == "Clinical Consultation":
    st.markdown("<div class='diagnostic-header'><h1>Diagnostic Consultation Mode</h1><p>Real-time multimodal analysis combining patient vitals and chest imaging.</p></div>", unsafe_allow_html=True)
    
    cin, cout = st.columns([1, 1.5])
    with cin:
        with st.form("consult_form"):
            st.markdown("#### Biometric Vitals")
            v1, v2 = st.columns(2)
            temp = v1.number_input("Temp (°C)", value=37.0, min_value=30.0, max_value=45.0)
            spo2 = v2.number_input("SpO2 (%)", value=98, min_value=50, max_value=100)
            sys_bp = v1.number_input("Systolic BP", value=120)
            hr = v2.number_input("Heart Rate", value=70)
            
            st.markdown("#### Clinical Manifestations")
            s1, s2, s3 = st.columns(3)
            cough = s1.checkbox("Cough")
            dyspnea = s2.checkbox("Dyspnea")
            fatigue = s3.checkbox("Fatigue")
            
            st.markdown("#### Imaging Integration")
            xray = st.file_uploader("Chest X-ray (Static/DICOM)", type=['png', 'jpg', 'jpeg'])
            
            run_btn = st.form_submit_button("Perform CDSS Analysis", use_container_width=True)
            
    if run_btn:
        with cout:
            with st.spinner("Executing Inference Engine..."):
                vitals = {"Temperature": temp, "SpO2": spo2, "SystolicBloodPressure": sys_bp, "Heartrate": hr, "Cough": cough, "Dyspnea": dyspnea, "Fatigue": fatigue}
                report = pipeline.analyze_live(vitals, xray)
            
            st.markdown(f"### Assessment: {report['severity']} Risk Profile")
            st.info(report['summary'])
            
            if xray:
                img_res = report['image_analysis']
                ix1, ix2 = st.columns([1, 1])
                ix1.image(xray, caption="Input Data", use_column_width=True)
                with ix2:
                    st.markdown(f"**Imaging Found:** {img_res['finding']}")
                    st.markdown(f"**AI Confidence:** {img_res['confidence']*100:.1f}%")
                    st.write(img_res['description'])
            
            st.divider()
            a_c, r_c, v_c = st.columns([1,1,1])
            with a_c:
                st.markdown("#### Active Clinical Alerts")
                for a in report['alerts']: st.warning(a)
            with r_c:
                st.markdown("#### Prescriptive Guidance")
                for r in report['recommendations']: st.success(r)
            with v_c:
                st.plotly_chart(ev.plot_individual_vitals(vitals, TH_COLORS), use_container_width=True)

st.markdown("---")
st.caption("NEUROCARE Analytical Platform © 2026 | Professional Clinical Decision Support System")
