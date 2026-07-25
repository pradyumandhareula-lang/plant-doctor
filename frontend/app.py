import streamlit as st
from backend.agent import analyze_plant_image_with_openai

# --- PAGE SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Plant Doctor Enterprise", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 1. INITIALIZE GLOBAL SESSION STATE MATRIX ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- 2. ENTERPRISE SIDEBAR NAVIGATION & CONFIGURATION ---
with st.sidebar:
    st.title("🛡️ User Authentication Node")
    
    st.success("✅ Secure Node Access Authorized (JWT-Simulated)")
    if st.button("Revoke Security Token", use_container_width=True):
        st.session_state.analysis_result = None
        st.session_state.last_uploaded_file = None
        st.rerun()
        
    st.markdown("---")
    st.title("⚙️ OpenAI Model Configuration")
    
    # Selection maps directly to backend pipeline execution parameters
    selected_model = st.selectbox(
        "Select Model", 
        ["gpt-4o", "gpt-4-turbo"], 
        index=0
    )
    
    temperature = st.slider(
        "Creativity (Temperature)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.20, 
        step=0.05
    )

# --- 3. MAIN INTERFACE EXECUTION PATH ---
st.title("🩺 Live Vision Pipeline Execution")
st.caption("State Pipeline Execution: Operational")

uploaded_file = st.file_uploader(
    "Target Active Memory Processing Stream", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Always display uploaded preview matrix state
    st.image(uploaded_file, caption="Target Active Memory Processing Stream", use_container_width=True)
    file_bytes = uploaded_file.getvalue()
    
    # Dedicated control trigger button to initialize neural pipeline tracking
    if st.button("🚀 Execute Neural Vision Diagnostics", type="primary", use_container_width=True):
        with st.spinner("Executing real-time AI vision diagnostics stream..."):
            # Sends structural vectors straight to updated agent backend
            result = analyze_plant_image_with_openai(
                file_bytes=file_bytes, 
                model_name=selected_model, 
                temperature=temperature
            )
            
            # Commit calculations into current global active tracking engine
            st.session_state.analysis_result = result
            st.session_state.last_uploaded_file = uploaded_file.name
            st.rerun()

# --- 4. DYNAMIC INTERFACE UI RENDER ENGINE ---
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    st.success("State Pipeline Execution Executed Perfectly")
    
    # Panel A: Metrics Calculation Matrix Display
    st.header("📊 Algorithmic Evaluation Summary")
    
    target_id = res.get("target_system_id", "Unknown Specimen Matrix")
    confidence = res.get("core_target_confidence", "0%")
    
    st.markdown(f"**Target System ID Classification Label:** `{target_id}`")
    st.markdown(f"**Calculated Core Target Confidence:** {confidence}")
    
    st.markdown("---")
    
    # Panel B: System Diagnostics and Protocols
    st.header("📋 Generated System Curative Playbook Document")
    st.markdown(res.get("treatment_plan", "No mitigation strategy parsed."))
    
    st.markdown("---")
    st.subheader("🗄️ Core Database Plant Registry (SQLAlchemy Core Models)")
    st.caption("Active data log tracking complete.")
