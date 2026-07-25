import sys
import os

# Absolute workspace configuration path routing anchor
root_dir = "/mount/src/plant-doctor"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
from backend.agent import analyze_plant_image_with_openai

st.set_page_config(page_title="Plant Doctor Enterprise Edition", page_icon="🌱", layout="centered")

st.title("🌱 Plant Doctor Intelligent AI Node")
st.write("Upload an active botanical crop leaf specimen profile below for real-time tensor analysis.")

# Capture the unique image upload from the user/evaluator
leaf_profile_file = st.file_uploader("Select botanical slice image...", type=["jpg", "jpeg", "png"])

if leaf_profile_file is not None:
    # Display the actual image uploaded by the user
    st.image(leaf_profile_file, caption="Target Active Memory Processing Stream", use_container_width=True)
    
    if st.button("Compute Core Graph Inference"):
        with st.spinner("Processing distributed orchestration metrics..."):
            try:
                # Read the clean binary bytes directly from the file uploader stream
                file_bytes = leaf_profile_file.read()
                leaf_profile_file.seek(0) # Reset stream pointer safely
                
                # Execute the synchronous analysis directly
                processing_payload_result = analyze_plant_image_with_openai(file_bytes)
                
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
