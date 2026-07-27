import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Plant Doctor AI", layout="wide")

# --- BACKEND API CONFIG ---
API_BASE_URL = "http://localhost:8000" # Update to your deployed FastAPI URL on Streamlit Cloud

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- SIDEBAR: AUTHENTICATION & NAVIGATION ---
st.sidebar.title("🌱 Plant Doctor AI")

if st.session_state.token is None:
    st.sidebar.subheader("Login / Sign Up")
    auth_mode = st.sidebar.radio("Choose Mode", ["Login", "Sign Up"])
    username_input = st.sidebar.text_input("Username")
    password_input = st.sidebar.text_input("Password", type="password")

    if auth_mode == "Login":
        if st.sidebar.button("Log In"):
            try:
                res = requests.post(f"{API_BASE_URL}/login", data={"username": username_input, "password": password_input})
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.token = data.get("access_token")
                    st.session_state.username = username_input
                    st.sidebar.success(f"Welcome, {username_input}!")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid credentials.")
            except Exception as e:
                st.sidebar.error(f"Auth server error: {e}")
    else:
        if st.sidebar.button("Sign Up"):
            try:
                res = requests.post(f"{API_BASE_URL}/register", json={"username": username_input, "password": password_input})
                if res.status_code in [200, 201]:
                    st.sidebar.success("Account created! Please log in.")
                else:
                    st.sidebar.error("Registration failed.")
            except Exception as e:
                st.sidebar.error(f"Auth server error: {e}")
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("Log Out"):
        st.session_state.token = None
        st.session_state.username = None
        st.rerun()

st.sidebar.markdown("---")
navigation = st.sidebar.selectbox(
    "Select Feature", 
    ["Single Image Diagnosis", "Plant Registry", "Weekly Photo Comparison"]
)

# ==============================================================================
# FEATURE 1: SINGLE IMAGE DIAGNOSIS (With UI & Truncation Fixes)
# ==============================================================================
if navigation == "Single Image Diagnosis":
    st.title("🩺 Single Image Diagnosis")
    st.write("Upload a leaf/plant image for immediate AI analysis.")

    col1, col2 = st.columns([1, 1.2]) # 1:1.2 ratio gives room for full text display

    with col1:
        st.header("Upload")
        uploaded_file = st.file_uploader("Select a clear leaf or plant image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            analyze_btn = st.button("🚀 Run Botanical Analysis", type="primary")

    with col2:
        st.header("Results")
        if uploaded_file is not None and analyze_btn:
            with st.spinner("Analyzing plant..."):
                try:
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
                    
                    response = requests.post(f"{API_BASE_URL}/analyze", files=files, headers=headers)

                    if response.status_code == 200:
                        data = response.json()

                        # Uses Markdown instead of st.metric to prevent 'He...' truncation
                        st.markdown(f"**Detected Species:** {data.get('species', 'N/A')}")
                        st.markdown(f"**Health Status:** {data.get('health_status', 'N/A')}")
                        st.markdown(f"**Confidence:** {data.get('confidence', 0)}%")

                        st.markdown("---")
                        st.subheader("📋 Recommended Treatment Plan")
                        treatments = data.get("treatment_plan", [])
                        if treatments:
                            for step in treatments:
                                st.write(f"- {step}")
                        else:
                            st.write("No specific treatments required.")
                    else:
                        st.error(f"API Error ({response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"Could not connect to backend: {e}")
        else:
            st.info("Upload an image and click 'Run Botanical Analysis' to see results.")

# ==============================================================================
# FEATURE 2: PLANT REGISTRY
# ==============================================================================
elif navigation == "Plant Registry":
    st.title("🪴 Plant Registry")
    st.write("Manage your registered plants and view historical health records.")

    if not st.session_state.token:
        st.warning("Please log in from the sidebar to access your plant registry.")
    else:
        st.subheader("Register a New Plant")
        with st.form("register_plant_form"):
            plant_name = st.text_input("Plant Nickname")
            species_input = st.text_input("Species (Optional)")
            submitted = st.form_submit_button("Add to Registry")

            if submitted and plant_name:
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    res = requests.post(
                        f"{API_BASE_URL}/registry/add", 
                        json={"name": plant_name, "species": species_input}, 
                        headers=headers
                    )
                    if res.status_code in [200, 201]:
                        st.success(f"Added {plant_name} to your registry!")
                    else:
                        st.error("Failed to add plant.")
                except Exception as e:
                    st.error(f"Server error: {e}")

        st.markdown("---")
        st.subheader("Your Registered Plants")
        try:
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.get(f"{API_BASE_URL}/registry/list", headers=headers)
            if res.status_code == 200:
                plants = res.json()
                if plants:
                    for p in plants:
                        with st.expander(f"🪴 {p.get('name')} ({p.get('species', 'Unknown Species')})"):
                            st.write(f"**ID:** {p.get('id')}")
                            st.write(f"**Added Date:** {p.get('created_at', 'N/A')}")
                else:
                    st.info("No registered plants found. Add one above!")
        except Exception as e:
            st.error(f"Could not load registry: {e}")

# ==============================================================================
# FEATURE 3: WEEKLY PHOTO COMPARISON TOOL
# ==============================================================================
elif navigation == "Weekly Photo Comparison":
    st.title("📊 Weekly Photo Comparison")
    st.write("Compare week-over-week plant growth and recovery status using dual-image vision analysis.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Week 1 (Baseline Image)")
        img_week1 = st.file_uploader("Upload Week 1 Photo", type=["jpg", "jpeg", "png"], key="w1")
        if img_week1:
            st.image(Image.open(img_week1), use_container_width=True)

    with col2:
        st.subheader("Week 2 (Current Image)")
        img_week2 = st.file_uploader("Upload Week 2 Photo", type=["jpg", "jpeg", "png"], key="w2")
        if img_week2:
            st.image(Image.open(img_week2), use_container_width=True)

    if img_week1 and img_week2:
        if st.button("🔍 Compare Growth & Recovery", type="primary"):
            with st.spinner("Analyzing side-by-side progression..."):
                try:
                    files = [
                        ("files", (img_week1.name, img_week1.getvalue(), img_week1.type)),
                        ("files", (img_week2.name, img_week2.getvalue(), img_week2.type))
                    ]
                    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
                    
                    res = requests.post(f"{API_BASE_URL}/compare", files=files, headers=headers)
                    if res.status_code == 200:
                        comp_data = res.json()
                        st.success("Comparison Complete!")
                        st.subheader("📈 AI Recovery Analysis")
                        st.write(comp_data.get("analysis", "No details returned."))
                    else:
                        st.error(f"Comparison failed ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
