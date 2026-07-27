import sys
import os
import requests
import streamlit as st
import threading
import uvicorn
import time

# --- 0. BACKGROUND FASTAPI RUNNER (FOR STREAMLIT CLOUD DEPLOYMENT) ---
def run_fastapi():
    try:
        from backend.main import app
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
    except Exception as e:
        print(f"FastAPI background server error: {e}")

# Check if FastAPI is already responding; if not, spin it up in a thread
@st.cache_resource
def start_backend():
    try:
        requests.get("http://127.0.0.1:8000/docs", timeout=1)
    except Exception:
        thread = threading.Thread(target=run_fastapi, daemon=True)
        thread.start()
        time.sleep(2) # Give uvicorn a moment to initialize database & routes

start_backend()

API_URL = "http://127.0.0.1:8000"


# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Plant Doctor AI",
    page_icon="🌿",
    layout="wide"
)


# --- 2. SIDEBAR: G-40 & TEMPERATURE SETTINGS & AUTH ---
with st.sidebar:
    st.header("⚙️ Settings")

    g40_setting = st.text_input(
        "G-40 Setting",
        value="G40-Default",
        help="Configure your G-40 parameter or system tag."
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.05,
        help="Controls output creativity vs determinism."
    )

    st.divider()

    # User Auth Session State Status
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

    if st.session_state["user_id"]:
        st.success(f"Logged in as: **{st.session_state['username']}**")
        if st.button("Log Out"):
            st.session_state["user_id"] = None
            st.session_state["username"] = None
            st.rerun()
    else:
        st.info("Not logged in")


# --- 3. UI HEADER ---
st.title("🌿 Plant Doctor AI Pathologist")
st.markdown("Upload a leaf or plant image to run automated botanical diagnosis.")
st.divider()


# --- 4. TABS NAVIGATION ---
tabs = st.tabs(["🔐 Auth", "🪴 Plant Registry", "🔍 AI Diagnosis", "📊 Weekly Check-In"])


# ---------------------------------------------------------
# TAB 1: USER AUTHENTICATION
# ---------------------------------------------------------
with tabs[0]:
    st.header("Account Management")
    auth_choice = st.radio("Choose Action", ["Login", "Register"])
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if auth_choice == "Register":
        if st.button("Create Account"):
            if username_input and password_input:
                try:
                    res = requests.post(f"{API_URL}/register", json={"username": username_input, "password": password_input})
                    if res.status_code == 200:
                        st.success("Account created successfully! Please log in.")
                    else:
                        st.error(res.json().get("detail", "Registration failed"))
                except Exception as e:
                    st.error(f"Cannot connect to backend: {str(e)}")
            else:
                st.warning("Please provide both username and password.")

    elif auth_choice == "Login":
        if st.button("Log In"):
            if username_input and password_input:
                try:
                    res = requests.post(f"{API_URL}/login", json={"username": username_input, "password": password_input})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["user_id"] = data["user_id"]
                        st.session_state["username"] = data["username"]
                        st.success(f"Welcome back, {data['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                except Exception as e:
                    st.error(f"Cannot connect to backend: {str(e)}")


# ---------------------------------------------------------
# TAB 2: PLANT REGISTRY
# ---------------------------------------------------------
with tabs[1]:
    st.header("My Plant Registry")
    if not st.session_state["user_id"]:
        st.warning("Please log in to view and register your plants.")
    else:
        with st.form("add_plant_form"):
            plant_name = st.text_input("Plant Name (e.g., Fiddle Leaf Fig)")
            species = st.text_input("Species (Optional)")
            submitted = st.form_submit_button("Add Plant")

            if submitted and plant_name:
                try:
                    res = requests.post(f"{API_URL}/plants", json={
                        "user_id": st.session_state["user_id"],
                        "plant_name": plant_name,
                        "species": species
                    })
                    if res.status_code == 200:
                        st.success(f"Added '{plant_name}' to your registry!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding plant: {str(e)}")

        # Fetch saved plants from FastAPI + SQLite
        try:
            res = requests.get(f"{API_URL}/plants/{st.session_state['user_id']}")
            if res.status_code == 200:
                plants = res.json().get("plants", [])
                if plants:
                    st.subheader("Your Registered Plants")
                    for p in plants:
                        st.write(f"- **{p['plant_name']}** ({p['species'] or 'Unknown species'}) — Registered on {p['created_at']}")
                else:
                    st.info("No plants registered yet.")
        except Exception as e:
            st.error(f"Failed to fetch plant registry: {str(e)}")


# ---------------------------------------------------------
# TAB 3: AI DIAGNOSIS (ROUTED THROUGH FASTAPI)
# ---------------------------------------------------------
with tabs[2]:
    if not st.session_state["user_id"]:
        st.warning("Please log in to run diagnoses.")
    else:
        try:
            res = requests.get(f"{API_URL}/plants/{st.session_state['user_id']}")
            user_plants = res.json().get("plants", []) if res.status_code == 200 else []
        except Exception:
            user_plants = []

        if not user_plants:
            st.info("Please register a plant in the 'Plant Registry' tab first.")
        else:
            plant_options = {p["plant_name"]: p["id"] for p in user_plants}
            selected_plant_name = st.selectbox("Select Registered Plant", list(plant_options.keys()))
            selected_plant_id = plant_options[selected_plant_name]

            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.subheader("📷 Image Upload")
                uploaded_file = st.file_uploader(
                    "Select a clear leaf image (JPG, JPEG, PNG)",
                    type=["jpg", "jpeg", "png"]
                )

                if uploaded_file is not None:
                    st.image(uploaded_file, caption="Target Image", use_container_width=True)

                    if st.button("🚀 Run Botanical Analysis", type="primary", use_container_width=True):
                        with st.spinner("Initializing Botanical Analysis Pipeline via FastAPI Backend..."):
                            try:
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                data = {"plant_id": selected_plant_id}

                                # POST request to FastAPI endpoint
                                response = requests.post(f"{API_URL}/api/diagnose", data=data, files=files)

                                if response.status_code == 200:
                                    st.session_state["analysis_result"] = response.json().get("data")
                                    st.success("Analysis complete!")
                                else:
                                    # Properly surfaces error states rather than rendering fake cards
                                    st.error(f"Diagnosis Failed: {response.json().get('detail', 'API Error')}")
                            except Exception as e:
                                st.error(f"Execution Error: {str(e)}")

            with col2:
                st.subheader("📊 Diagnostic Results")
                if "analysis_result" in st.session_state and st.session_state["analysis_result"]:
                    res = st.session_state["analysis_result"]

                    species = res.get("target_system_id", "Unknown Specimen")
                    confidence = res.get("core_target_confidence", "N/A")
                    treatment = res.get("treatment_plan", "No treatment plan returned.")

                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric(label="Detected Species / Condition", value=species)
                    with m_col2:
                        st.metric(label="Confidence Level", value=confidence)

                    st.markdown("---")
                    st.markdown("### 🪴 Recommended Treatment Plan")
                    st.markdown(treatment)
                else:
                    st.info("Upload an image on the left and click **Run Botanical Analysis** to see results.")


# ---------------------------------------------------------
# TAB 4: WEEKLY CHECK-IN (PROGRESS COMPARISON)
# ---------------------------------------------------------
with tabs[3]:
    st.header("Weekly Progress Comparison")
    st.write("Upload a previous week's photo alongside a current photo to evaluate progress.")

    col1, col2 = st.columns(2)
    with col1:
        prev_file = st.file_uploader("Previous Photo (Week 1)", type=["jpg", "jpeg", "png"], key="prev")
    with col2:
        curr_file = st.file_uploader("Current Photo (Week 2)", type=["jpg", "jpeg", "png"], key="curr")

    if prev_file and curr_file and st.button("Compare Weekly Progress"):
        with st.spinner("Analyzing progress between photos via FastAPI backend..."):
            try:
                files = {
                    "previous_photo": (prev_file.name, prev_file.getvalue(), prev_file.type),
                    "current_photo": (curr_file.name, curr_file.getvalue(), curr_file.type)
                }
                response = requests.post(f"{API_URL}/api/compare", files=files)

                if response.status_code == 200:
                    st.subheader("Progress Report")
                    st.markdown(response.json().get("data"))
                else:
                    st.error(f"Comparison failed: {response.json().get('detail', 'Error')}")
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")


# --- FOOTER ---
st.divider()
st.caption("Plant Doctor Enterprise | Powered by Streamlit, FastAPI & Gemini API")
