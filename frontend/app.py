import streamlit as st
import requests

st.set_page_config(page_title="Plant Doctor Suite", page_icon="🌿", layout="wide")

st.title("🌿 AI Plant Doctor")
st.write("Upload a photo of any plant to generate an instant AI diagnostic report.")

tab1, tab2, tab3 = st.tabs(["🔍 New Scan", "📜 Scan History", "📅 Care Reminder"])

with tab1:
    uploaded_file = st.file_uploader("Choose a plant photo...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Selected Foliage Photo", use_container_width=False)
        
        if st.button("Run Plant Diagnosis 🩺"):
            with st.spinner("AI Agent analyzing plant details..."):
                try:
                    # Direct API reference URL string 
                    
                    backend_url = "https://pradyuman-dhareula-plant-doctor-backend.hf.space/diagnose"
                    
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(backend_url, files=files)
                    
                    if response.status_code == 200:
                        st.success("Analysis Complete!")
                        result = response.json()
                        
                        st.subheader(f"Species: {result.get('species', 'Unknown')}")
                        st.write(f"**Condition:** {result.get('condition', 'N/A')}")
                        st.write(f"**Confidence:** {result.get('confidence', 'N/A')}")
                        
                        st.write("**Care Plan:**")
                        for step in result.get('care_plan', []):
                            st.write(f"- {step}")
                    else:
                        st.error(f"Backend error: Received status code {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Failed to connect to the backend: {e}")
