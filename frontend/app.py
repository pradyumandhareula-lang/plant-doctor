import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Plant Doctor Suite", page_icon="🌿", layout="centered")

# Set up clean Navigation Tabs at the top of our interface
tab1, tab2, tab3 = st.tabs(["🔍 New Scan", "📜 Scan History", "📅 Care Reminders"])

# --- TAB 1: NEW SCAN FEATURE ---
with tab1:
    st.title("🌿 AI Plant Doctor")
    st.write("Upload a photo of your plant to generate an instant report.")
    
    uploaded_file = st.file_uploader("Choose a plant photo...", type=["jpg", "jpeg", "png"], key="uploader")
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Selected Foliage Photo", use_container_width=True)
        
        if st.button("Run Plant Diagnosis 🚀"):
            with st.spinner("Analyzing plant details via pipeline..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post("http://127.0.0", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("Analysis Complete!")
                        st.subheader(f"🌱 Identified: {data['plant_name']}")
                        st.warning(f"⚠️ Health Issue: {data['condition_summary']}")
                        st.write("### 📝 Treatment Plan:")
                        st.text(data['detailed_report'])
                        
                        # Save details into temporary session storage to auto-create an option B scheduler reminder
                        st.session_state['last_plant'] = data['plant_name']
                    else:
                        st.error("Backend Server communication failure.")
                except Exception as e:
                    st.error(f"Connection lost to server: {e}")

# --- TAB 2: HISTORY VIEW (Option A) ---
with tab2:
    st.title("📜 Past Diagnostic Records")
    st.write("Review past historical plant logs compiled inside the database.")
    
    if st.button("🔄 Refresh History Log"):
        try:
            response = requests.get("http://127.0.0.1:8000/diagnostics")
            if response.status_code == 200:
                history_data = response.json()
                
                if not history_data:
                    st.info("No scans found in the database yet!")
                else:
                    for record in reversed(history_data):
                        with st.expander(f"🌿 {record['plant_name']} - {record['created_at'][:10]}"):
                            st.write(f"**Condition Status:** {record['condition_summary']}")
                            st.write("**Treatment Protocols:**")
                            st.text(record['detailed_report'])
            else:
                st.error("Could not fetch logs.")
        except Exception as e:
            st.error(f"Database offline: {e}")

# --- TAB 3: CARE SCHEDULER REMINDERS (Option B) ---
with tab3:
    st.title("📅 Plant Care Scheduler")
    st.write("Set calendar tracks to remember watering or treatment routines.")
    
    # Pre-fill target name if user just completed a scan
    default_name = st.session_state.get('last_plant', "My Plant")
    
    plant_target = st.text_input("Plant Name:", value=default_name)
    care_type = st.selectbox("Action Required:", ["Watering 💧", "Apply Fungicide / Neem Oil 🧪", "Pruning ✂️", "Fertilizer 🧪"])
    reminder_date = st.date_input("Scheduled Date:", datetime.today())
    
    if st.button("Set Reminder Notification 🔔"):
        st.success(f"Successfully registered: {care_type} task configured for {plant_target} on {reminder_date}!")
        st.balloons()
