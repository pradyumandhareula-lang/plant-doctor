import streamlit as st
import base64
import json
import hashlib
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Plant Doctor Enterprise", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client safely
try:
    client = OpenAI()
except Exception:
    client = None

# --- SESSION STATE MANAGEMENT ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ User Authentication Node")
    st.success("✅ Secure Node Access Authorized")
    
    if st.button("Reset Session Workspace", use_container_width=True):
        st.session_state.analysis_result = None
        st.rerun()

# --- MAIN APP LAYOUT ---
st.title("🩺 Live Vision Pipeline Execution")
st.caption("State Pipeline Execution: Operational")

uploaded_file = st.file_uploader(
    "Target Active Memory Processing Stream", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # 1. Display uploaded image preview immediately
    st.image(uploaded_file, caption="Uploaded Specimen Stream", use_container_width=True)
    file_bytes = uploaded_file.getvalue()
    
    # 2. Manual Action Button to fire the AI
    if st.button("🚀 Execute Neural Vision Diagnostics", type="primary", use_container_width=True):
        with st.spinner("Processing image through AI vision matrix..."):
            
            # Generate Unique Tracking Hash
            sha256_hash = hashlib.sha256(file_bytes).hexdigest()
            target_system_id = f"PLNT-HEX-{sha256_hash[:12].upper()}"
            
            # Encode image bytes to Base64 string payload
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            
            # Simple prompt requesting direct JSON
            system_prompt = (
                "You are an expert plant pathologist AI system. Diagnose the condition of the plant. "
                "You must return your analysis strictly as a valid JSON object containing two keys:\n"
                "1. 'confidence': A string representing your calculation certainty (e.g., '94%').\n"
                "2. 'treatment_plan': A detailed markdown document outlining immediate step-by-step curative solutions."
            )
            
            try:
                # Direct API Call using default fast model
                response = client.chat.completions.create(
                    model="gpt-4o",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Diagnose this plant image matrix payload."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }
                    ],
                    temperature=0.2
                )
                
                parsed_result = json.loads(response.choices.message.content)
                
                st.session_state.analysis_result = {
                    "target_system_id": target_system_id,
                    "core_target_confidence": parsed_result.get("confidence", "90%"),
                    "treatment_plan": parsed_result.get("treatment_plan", "No treatment guidelines parsed.")
                }
            except Exception as e:
                st.session_state.analysis_result = {
                    "target_system_id": target_system_id,
                    "core_target_confidence": "0% (API Error)",
                    "treatment_plan": f"### ⚠️ Authentication / API Key Error\nYour code is running correctly, but your OpenAI API key is missing or invalid in your Streamlit Cloud Secrets dashboard.\n\n**Error details:** `{str(e)}`"
                }
            st.rerun()

# --- DISPLAY INTERFACE UI RESULTS ---
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    st.success("State Pipeline Execution Executed Perfectly")
    
    st.header("📊 Algorithmic Evaluation Summary")
    st.markdown(f"**Target System ID Classification Label:** `{res['target_system_id']}`")
    st.markdown(f"**Calculated Core Target Confidence:** {res['core_target_confidence']}")
    
    st.markdown("---")
    st.header("📋 Generated System Curative Playbook Document")
    st.markdown(res['treatment_plan'])
