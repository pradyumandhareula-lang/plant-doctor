import sys
import os
import time

# --- 1. DYNAMIC PATH ROUTING ---
# Ensures Python can locate 'backend' regardless of working directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st

# --- 2. STREAMLIT SECRETS INTEGRATION ---
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Import agent vision function safely from backend
try:
    from backend.agent import analyze_plant_image
except ImportError:
    st.error("Failed to import `analyze_plant_image` from `backend.agent`. Ensure your directory structure is intact.")

# --- 3. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Plant Doctor AI",
    page_icon="🌿",
    layout="wide"
)

# --- 4. SESSION STATE INITIALIZATION ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- 5. UI HEADER ---
st.title("🌿 Plant Doctor AI Pathologist")
st.markdown("Upload a leaf or plant image to run automated botanical diagnosis and receive a detailed treatment plan.")

st.divider()

# --- 6. MAIN CONTENT LAYOUT ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📷 Image Upload")
    uploaded_file = st.file_uploader(
        "Select a clear leaf image (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Target Image", use_container_width=True)
        
        if st.button("🚀 Run Botanical Analysis", type="primary", use_container_width=True):
            with st.spinner("Initializing Botanical Analysis Pipeline..."):
                try:
                    # Read file bytes directly
                    image_bytes = uploaded_file.getvalue()
                    
                    # Call AI backend agent
                    result = analyze_plant_image(image_bytes=image_bytes)
                    st.session_state.analysis_result = result
                    st.success("Analysis complete!")
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

with col2:
    st.subheader("📋 Diagnostic Results")
    
    if st.session_state.analysis_result:
        res = st.session_state.analysis_result
        
        # Display Key Information Metrics
        species = res.get("target_system_id", "Unknown Specimen")
        confidence = res.get("core_target_confidence", "N/A")
        treatment = res.get("treatment_plan", "No treatment plan returned.")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Detected Species / Condition", value=species)
        with m_col2:
            st.metric(label="Confidence Level", value=confidence)
            
        st.markdown("---")
        st.markdown("### 🪴 Recommended Treatment Plan")
        st.markdown(treatment)
        
    else:
        st.info("Upload an image on the left and click **Run Botanical Analysis** to view results here.")

# Footer
st.divider()
st.caption("Plant Doctor Enterprise | Powered by Streamlit & Gemini API")
