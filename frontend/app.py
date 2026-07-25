import streamlit as st
from backend.main import diagnose_plant
import requests
from PIL import Image
import io

# Set page configurations
st.set_page_config(page_title="Plant Doctor Suite", page_icon="🌱", layout="centered")

st.title("🌱 AI Plant Doctor")
st.write("Upload a photo of your plant to generate an instant diagnostic")

# Navigation Tabs matching layout design blueprint
tab1, tab2, tab3 = st.tabs(["🔍 New Scan", "📜 Scan History", "🏥 Care Reminders"])

with tab1:
    uploaded_file = st.file_uploader("Choose a plant photo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded plant image visually on screen
        st.image(uploaded_file, caption="Selected Foliage Photo", use_container_width=True)
        
        if st.button("Run Plant Diagnosis 🚀"):
            with st.spinner("Analyzing plant details via pipeline..."):
                try:
                    data = diagnose_plant(uploaded_file)

                        # Render matching layout items dynamically from main.py return dictionary
                        st.success(f"✅ {data.get('status')}")
                        st.subheader(f"🫘 Identified Condition: {data.get('label')}")
                        st.warning(f"📊 Confidence Level: {data.get('confidence')}%")
                        
                        st.write("### 📋 Actionable Treatment Plan:")
                        st.info(data.get("treatment_plan"))
                        
                        # Save details into temporary session state storage
                        st.session_state['last_plant'] = data.get('label')
                   
                 
                except Exception as e:
                st.error(f"Connection lost to server: {e}")

with tab2:
    st.title("📜 Past Diagnostic Records")
    st.write("Review past historical plant logs compiled inside the system.")
    st.info("Scan history will populate dynamically once saved to the database backend.")

with tab3:
    st.title("🏥 Care Reminders")
    st.write("Keep track of your watering, pruning, and nutrition schedules.")
    st.info("Reminders panel is configured to read updates periodically.")
