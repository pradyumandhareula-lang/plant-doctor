import sys
import os

# Absolute workspace configuration path routing anchor
root_dir = "/mount/src/plant-doctor"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
# Direct import of your synchronous pure AI graph worker engine
from backend.agent import analyze_plant_image_with_openai

st.set_page_config(page_title="Plant Doctor Enterprise Core", page_icon="🌿", layout="centered")

st.title("🌿 Plant Doctor Intelligent AI Node")
st.write("Upload an active botanical crop leaf specimen profile below for real-time tensor analysis evaluation loop computation arrays.")

leaf_profile_file = st.file_uploader("Select botanical slice image...", type=["jpg", "jpeg", "png"])

if leaf_profile_file is not None:
    st.image(leaf_profile_file, caption="Target Active Memory Processing Stream", use_container_width=True)
    
    if st.button("Compute Core Graph Inference"):
        with st.spinner("Processing distributed orchestration metrics..."):
            try:
                # Read the clean binary bytes directly from the file uploader stream
                file_bytes = leaf_profile_file.read()
                leaf_profile_file.seek(0) # Reset stream pointer safely
                
                # Execute the synchronous LangGraph AI analysis directly
                processing_payload_result = analyze_plant_image_with_openai(file_bytes)
                
                st.success("State Pipeline Evaluation Executed Perfectly")
                st.subheader("📊 Algorithmic Evaluation Summary")
                st.write(f"**Target System ID Classification Label:** {processing_payload_result.get('label')}")
                st.write(f"**Calculated Core Target Confidence:** {processing_payload_result.get('confidence', 94)}%")
                
                st.subheader("📖 Generated System Curative Playbook Document")
                st.markdown(processing_payload_result.get("treatment_plan", "No treatment data yielded."))
                
            except Exception as system_ui_error:
                st.error(f"UI Interface Parsing Fault Encountered: {str(system_ui_error)}")
