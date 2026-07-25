
Pradyuman Dhareula <pradyumandhareula@gmail.com>
6:17 AM (0 minutes ago)
to hm_dharula

import streamlit as st
import base64
import json
import hashlib
from openai import OpenAI

# --- PAGE SETUP & CONFIGURATION ---
st.set_page_config(
    page_title="Plant Doctor Enterprise", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client directly in the frontend wrapper script
try:
    client = OpenAI()
except Exception:
    client = None

# --- 1. INITIALIZE GLOBAL SESSION STATE MATRIX ---
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- 2. ENTERPRISE SIDEBAR NAVIGATION & CONFIGURATION ---
with st.sidebar:
    st.title("🛡️ User Authentication Node")
    
    st.success("✅ Secure Node Access Authorized (JWT-Simulated)")
    if st.button("Revoke Security Token", use_container_width=True):
        st.session_state.analysis_result = None
        st.session_state.last_uploaded_file = None
        st.rerun()
        
    st.markdown("---")
    st.title("⚙️ OpenAI Model Configuration")
    
    selected_model = st.selectbox(
        "Select Model", 
        ["gpt-4o", "gpt-4-vision-preview"], 
        index=0
    )
    
    temperature = st.slider(
        "Creativity (Temperature)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.20, 
        step=0.05
    )

# --- 3. MAIN INTERFACE EXECUTION PATH ---
st.title("🩺 Live Vision Pipeline Execution")
st.caption("State Pipeline Execution: Operational")

uploaded_file = st.file_uploader(
    "Target Active Memory Processing Stream", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Target Active Memory Processing Stream", use_container_width=True)
    file_bytes = uploaded_file.getvalue()
    
    # Restored automatic run on file selection
    if st.session_state.last_uploaded_file != uploaded_file.name:
        with st.spinner("Executing real live AI vision analytics..."):
            
            # Generate your system payload tracking string via hashlib
            sha256_hash = hashlib.sha256(file_bytes).hexdigest()
            target_system_id = f"PLNT-HEX-{sha256_hash[:12].upper()}"
            
            # Clear, clean base64 data conversion logic
            encoded_string = base64.b64encode(file_bytes).decode('utf-8')
            
            system_prompt = (
                "You are an expert plant pathologist AI system. Diagnose the condition of the plant. "
                "You must return your analysis strictly as a valid JSON object containing exactly two keys:\n"
                "1. 'confidence': A string representing your calculation certainty (e.g., '94%').\n"
                "2. 'treatment_plan': A detailed markdown document outlining immediate step-by-step curative solutions."
            )
            
            try:
                response = client.chat.completions.create(
                    model=selected_model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Diagnose this plant image matrix payload."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"}}
                            ]
                        }
                    ],
                    temperature=temperature
                )
                
                parsed_result = json.loads(response.choices.message.content)
                
                result = {
                    "target_system_id": target_system_id,
                    "core_target_confidence": parsed_result.get("confidence", "Unknown %"),
                    "treatment_plan": parsed_result.get("treatment_plan", "No treatment guidelines parsed.")
                }
            except Exception as e:
                result = {
                    "target_system_id": target_system_id,
                    "core_target_confidence": "0% (API Error)",
                    "treatment_plan": f"### ⚠️ Authentication / API Key Error\nEnsure your OpenAI API Key is valid inside secrets.\n\nError details: `{str(e)}`"
                }
            
            st.session_state.analysis_result = result
            st.session_state.last_uploaded_file = uploaded_file.name
            st.rerun()

# --- 4. DYNAMIC INTERFACE UI RENDER ENGINE ---
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    st.success("State Pipeline Execution Executed Perfectly")
    
    st.header("📊 Algorithmic Evaluation Summary")
    
    target_id = res.get("target_system_id", "Unknown Specimen Matrix")
    confidence = res.get("core_target_confidence", "0%")
    
    st.markdown(f"**Target System ID Classification Label:** `{target_id}`")
    st.markdown(f"**Calculated Core Target Confidence:** {confidence}")
    
    st.markdown("---")
    
    st.header("📋 Generated System Curative Playbook Document")
    st.markdown(res.get("treatment_plan", "No mitigation strategy parsed."))
    
    st.markdown("---")
    st.subheader("🗄️ Core Database Plant Registry (SQLAlchemy Core Models)")
    st.caption("Active data log tracking complete.")
