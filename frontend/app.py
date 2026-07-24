import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Plant Doctor Suite",
    page_icon="🌿",
    layout="wide"
)

# 2. Header Elements
st.title("🌿 AI Plant Doctor")
st.write("Upload a photo of any plant to generate an instant AI diagnosis.")

# 3. Tab Structure Layout
tab1, tab2, tab3 = st.tabs([
    "🔍 New Scan", 
    "📜 Scan History", 
    "📅 Care Reminder"
])

# 4. Diagnostic Tab Logic
with tab1:
    uploaded_file = st.file_uploader(
        "Choose a plant photo...",
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Uploaded Plant",
            use_container_width=True
        )
        
        if st.button("Run Plant Diagnosis 🩺"):
            with st.spinner("Analyzing plant..."):
                # Clean route linking straight to your running FastAPI backend
                backend_url = "https://pradyuman-dhareula-plant-doctor.hf.space"
                
                try:
                    # Construct multipart payload for file transfers
                    files = {
                        "file": (
                            uploaded_file.name, 
                            uploaded_file.getvalue(), 
                            uploaded_file.type
                        )
                    }
                    
                    # Process request payload to Hugging Face
                    response = requests.post(backend_url, files=files, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Diagnosis Complete!")
                        
                        # Structured metric design for your capstone presentation
                        st.metric(label="Identified Species", value=result.get("species", "Unknown"))
                        st.subheader(f"Condition: {result.get('condition', 'N/A')}")
                        st.write(f"Confidence Level: **{result.get('confidence', '0%')}**")
                        
                        st.write("### Recommended Care Plan:")
                        for step in result.get("care_plan", []):
                            st.write(f"- {step}")
                    else:
                        st.error(f"Backend Error: Status code {response.status_code}")
                        st.json(response.text)
                        
                except Exception as e:
                    st.error(f"Could not connect to backend server: {e}")
