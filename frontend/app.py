import streamlit as st
import requests

st.set_page_config(page_title="Plant Doctor Suite", page_icon="🌱", layout="wide")

st.title("🌱 AI Plant Doctor")
st.write("Upload a photo of your plant to generate an instant diagnostic report.")

tab1, tab2, tab3 = st.tabs(["🔍 New Scan", "📋 Scan History", "📅 Care Reminders"])

with tab1:
    uploaded_file = st.file_uploader("Choose a plant photo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Selected Foliage Photo", use_container_width=False)
        
        if st.button("Run Plant Diagnosis 🩺"):
            with st.spinner("Analyzing plant details via pipeline..."):
                 try:
            backend_url = "https://pradyuman-dhareula-plant-doctor-backend.hf.space/predict"
            files = {"file": uploaded_file.getvalue()}
            response = requests.post(backend_url, files=files)
            if response.status_code == 200:
    st.success("Analysis Complete!")
    st.write(response.json().get("diagnosis", "No diagnosis found."))
    else:
    st.error(f"Backend error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")


with tab2:
    st.header("📋 Past Diagnostic Records")
    st.write("Review past historical plant logs compiled inside the system.")
    st.info("Scan history will populate dynamically once saved to the database backend configuration.")
