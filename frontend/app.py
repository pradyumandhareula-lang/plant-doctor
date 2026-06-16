import streamlit as st
import base64
from openai import OpenAI

# 1. Page Configuration Setup
st.set_page_config(page_title="Plant Doctor Suite", page_icon="🌱", layout="wide")

st.title("🌱 AI Plant Doctor")
st.write("Upload a photo of your plant to generate an instant diagnostic report.")

# Navigation Tabs matching your original blueprint
tab1, tab2, tab3 = st.tabs(["🔍 New Scan", "📋 Scan History", "📅 Care Reminders"])

with tab1:
    uploaded_file = st.file_uploader("Choose a plant photo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image visually on screen
        st.image(uploaded_file, caption="Selected Foliage Photo", use_container_width=True)
        
        if st.button("Run Plant Diagnosis 🩺"):
            with st.spinner("Analyzing plant details via pipeline..."):
                try:
                    # Fetch credentials from Streamlit Secrets securely
                    if "OPENAI_API_KEY" not in st.secrets:
                        st.error("Missing OpenAI API Key! Please add it to your Streamlit secrets panel.")
                    else:
                        # Initialize OpenAI Client
                        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                        
                        # Encode image bytes to base64 string for OpenAI API injection
                        bytes_data = uploaded_file.getvalue()
                        base64_image = base64.b64encode(bytes_data).decode("utf-8")
                        
                        # Make unified Vision processing API call
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": "Identify the plant species, diagnose its health status, provide a confidence metric, and outline an actionable recovery plan."},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                    ],
                                }
                            ],
                            max_tokens=600,
                        )
                        
                        # Display Output Results
                        st.success("Analysis Complete!")
                        st.markdown(response.choices[0].message.content)
                        
                except Exception as e:
                    st.error(f"An internal exception occurred during pipeline evaluation: {str(e)}")
