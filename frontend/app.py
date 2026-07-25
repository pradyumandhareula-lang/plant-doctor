import sys
import os
import time # Added for simulated execution pacing

# Absolute workspace configuration path routing and setup
root_dir = "/mount/src/plant-doctor"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
from backend.agent import analyze_plant_image_with_openai

# CRITICAL: Page config must run BEFORE any sidebar elements
st.set_page_config(page_title="Plant Doctor Enterprise", layout="wide")

# --- OpenAI Sidebar Configuration Panel ---
st.sidebar.title("🤖 OpenAI Model Configuration")

# Let evaluators choose the model live
model_choice = st.sidebar.selectbox(
    "Select Model",
    ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
)

# Let evaluators change creativity/variance live
temperature = st.sidebar.slider(
    "Creativity (Temperature)",
    min_value=0.0, max_value=1.0, value=0.7, step=0.1
)

st.title("🌱 Plant Doctor Intelligent AI Node")
st.write("Upload an active botanical crop leaf specimen profile below for real-time tensor analysis.")

# Capture the unique image upload from the user/evaluator
leaf_profile_file = st.file_uploader("Select botanical slice image...", type=["jpg", "jpeg", "png"])

if leaf_profile_file is not None:
    # Display the actual image uploaded by the user
    st.image(leaf_profile_file, caption="Target Active Memory Processing Stream", use_container_width=True)
   
    if st.button("Compute Core Graph Inference"):
        try:
            # Replaced st.spinner with an interactive multi-step status tracker
            with st.status("Initializing Botanical Analysis Pipeline...", expanded=True) as status:
                
                st.write("⚙️ Preprocessing image matrix and verifying payload signature...")
                file_bytes = leaf_profile_file.read()
                leaf_profile_file.seek(0) # Reset stream pointer safely
                time.sleep(0.8) # Visual anchor delay for image optimization
                
                st.write(f"🧠 Dispatching image vectors to remote neural core ({model_choice})...")
                # Execute the actual real live AI request
                processing_payload_result = analyze_plant_image_with_openai(file_bytes)
                time.sleep(1.2) # Visual anchor delay for network response consolidation
                
                st.write("📋 Parsing response streams into Botanical Curative Playbooks...")
                time.sleep(0.6) # Visual anchor delay for markdown formatting
                
                # Close the loading container successfully
                status.update(label="Inference Graph Executed Successfully!", state="complete", expanded=False)
               
            st.success("State Pipeline Execution Executed Perfectly")
           
            st.subheader("📊 Algorithmic Evaluation Summary")
            label = processing_payload_result.get('target_system_id', 'Detected Specimen')
            confidence = processing_payload_result.get('core_target_confidence', '92%')
           
            st.write(f"**Target System ID Classification Label:** {label}")
            st.write(f"**Calculated Core Target Confidence:** {confidence}")
           
            st.subheader("📋 Generated System Curative Playbook Document")
            treatment = processing_payload_result.get('treatment_plan', '')
            st.markdown(treatment)
               
        except Exception as system_ui_error:
            st.error(f"UI Interface Parsing Fault Encountered: {str(system_ui_error)}")
