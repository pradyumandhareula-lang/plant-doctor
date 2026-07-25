import sys
import os

# 1. Absolute path injection so Python can find your 'backend' folder
root_dir = "/mount/src/plant-doctor"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st
from backend.main import diagnose_plant

# 2. Configure the Streamlit Page
st.set_page_config(page_title="Plant Doctor AI", page_icon="🌱", layout="centered")

st.title("🌱 Plant Doctor AI Capstone")
st.write("Upload an image of a plant leaf to detect diseases and get a treatment plan.")

# 3. File Uploader Component
uploaded_file = st.file_uploader("Choose a plant leaf image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image to the user
    st.image(uploaded_file, caption="Uploaded Leaf Image", use_container_width=True)
    
    # Diagnosis Button Trigger
    if st.button("Analyze Plant Health"):
        with st.spinner("Running AI Graph Diagnosis..."):
            try:
                # Call your backend controller function directly
                result = diagnose_plant(uploaded_file)
                
                # Render the diagnostic outputs cleanly
                st.success(result.get("status", "Analysis Completed"))
                
                st.subheader("📋 Diagnostic Results")
                st.write(f"**Condition / Label:** {result.get('label', 'Unknown')}")
                st.write(f"**Confidence Level:** {result.get('confidence', 0)}%")
                
                st.subheader("🛠️ Recommended Treatment Plan")
                st.markdown(result.get("treatment_plan", "No plan provided."))
                
            except Exception as e:
                st.error(f"An error occurred during execution: {str(e)}")
