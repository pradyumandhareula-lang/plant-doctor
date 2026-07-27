import streamlit as st
from PIL import Image
import google.generativeai as genai
import json

# Page setup
st.set_page_config(page_title="Plant Doctor AI", page_icon="🌱", layout="wide")

# --- CONFIGURE GEMINI API DIRECTLY ---
# Replace with your actual Gemini API key
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

# System prompt for structured vision diagnosis
SYSTEM_PROMPT = """
You are an expert botanical doctor AI. Analyze the uploaded plant image and identify:
1. Plant species (common and scientific name). If no plant/flower/leaf is present, set species to 'Unknown'.
2. Health status and confidence percentage (0-100%).
3. Recommended treatment plan (bullet points for Sunlight, Watering, and Care).

Respond strictly in valid JSON format matching this schema:
{
    "species": "Plant Name",
    "health_status": "Healthy / Diseased",
    "confidence": 95,
    "treatment_plan": [
        "Sunlight: ...",
        "Watering: ...",
        "Care: ..."
    ]
}
"""

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "users" not in st.session_state:
    st.session_state.users = {"demo": "password123"} # Default test account
if "registry" not in st.session_state:
    st.session_state.registry = []

# ==============================================================================
# SCREEN 1: LOGIN / SIGN UP GATEWAY
# ==============================================================================
if not st.session_state.logged_in:
    col_a, col_b, col_c = st.columns([1, 2, 1])
    
    with col_b:
        st.title("🌱 Plant Doctor AI")
        st.caption("Welcome! Please log in or create an account to access botanical diagnostics.")
        
        tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])

        with tab_login:
            st.subheader("Login to your account")
            login_user = st.text_input("Username", key="l_user")
            login_pass = st.text_input("Password", type="password", key="l_pass")
            
            if st.button("Log In", type="primary", use_container_width=True):
                if login_user in st.session_state.users and st.session_state.users[login_user] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab_signup:
            st.subheader("Create a new account")
            signup_user = st.text_input("Choose Username", key="s_user")
            signup_pass = st.text_input("Choose Password", type="password", key="s_pass")
            
            if st.button("Create Account", use_container_width=True):
                if signup_user in st.session_state.users:
                    st.error("Username already exists!")
                elif signup_user and signup_pass:
                    st.session_state.users[signup_user] = signup_pass
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Please fill in all fields.")

# ==============================================================================
# SCREEN 2: MAIN DASHBOARD (AFTER LOGIN)
# ==============================================================================
else:
    # Top Header & User Info
    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        st.title("🌱 Plant Doctor AI")
    with top_col2:
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    st.markdown("---")

    # Main Option Tabs (3 Features to Choose From)
    tab1, tab2, tab3 = st.tabs([
        "🩺 Single Image Diagnosis", 
        "🪴 Plant Registry", 
        "📊 Weekly Photo Comparison"
    ])

    # --------------------------------------------------------------------------
    # OPTION 1: SINGLE IMAGE DIAGNOSIS
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("Single Image Diagnosis")
        st.write("Upload a leaf or plant image for immediate AI health analysis.")

        col1, col2 = st.columns([1, 1.2])

        with col1:
            st.markdown("### Upload Image")
            uploaded_file = st.file_uploader("Select a plant image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"], key="diag_file")
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
                analyze_btn = st.button("🚀 Run Botanical Analysis", type="primary", use_container_width=True)

        with col2:
            st.markdown("### Results")
            if uploaded_file is not None and analyze_btn:
                with st.spinner("Analyzing plant..."):
                    try:
                        # Image compression to keep payloads fast
                        img = Image.open(uploaded_file)
                        img.thumbnail((800, 800))

                        # Call Gemini Model
                        model = genai.GenerativeModel(
                            model_name="gemini-flash",
                            system_instruction=SYSTEM_PROMPT
                        )
                        
                        response = model.generate_content(
                            [img, "Analyze this plant image."],
                            generation_config={
                                "response_mime_type": "application/json",
                                "temperature": 0.2
                            }
                        )

                        data = json.loads(response.text)

                        # Display results without truncation
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

                    except Exception as e:
                        st.error(f"Error processing diagnosis: {e}")
            else:
                st.info("Upload an image on the left and click 'Run Botanical Analysis'.")

    # --------------------------------------------------------------------------
    # OPTION 2: PLANT REGISTRY
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("Plant Registry")
        st.write("Keep track of your personal plant collection.")

        with st.form("add_plant_form"):
            st.markdown("#### Register a New Plant")
            p_name = st.text_input("Plant Nickname (e.g., 'Monstera in Living Room')")
            p_species = st.text_input("Species (Optional)")
            sub_btn = st.form_submit_button("Add to Registry")

            if sub_btn and p_name:
                entry = {
                    "owner": st.session_state.username,
                    "name": p_name,
                    "species": p_species if p_species else "Unknown Species"
                }
                st.session_state.registry.append(entry)
                st.success(f"Added '{p_name}' to your registry!")

        st.markdown("---")
        st.markdown("#### Your Saved Plants")
        user_plants = [p for p in st.session_state.registry if p["owner"] == st.session_state.username]

        if user_plants:
            for idx, item in enumerate(user_plants, 1):
                with st.expander(f"🪴 {idx}. {item['name']} — ({item['species']})"):
                    st.write(f"**Registered By:** {item['owner']}")
        else:
            st.info("No plants registered yet. Use the form above to add one.")

    # --------------------------------------------------------------------------
    # OPTION 3: WEEKLY PHOTO COMPARISON
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("Weekly Photo Comparison")
        st.write("Compare side-by-side plant images over time to evaluate growth or recovery.")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("#### Week 1 (Baseline)")
            w1_file = st.file_uploader("Upload Week 1 Photo", type=["jpg", "jpeg", "png"], key="w1_u")
            if w1_file:
                st.image(Image.open(w1_file), use_container_width=True)

        with c2:
            st.markdown("#### Week 2 (Current)")
            w2_file = st.file_uploader("Upload Week 2 Photo", type=["jpg", "jpeg", "png"], key="w2_u")
            if w2_file:
                st.image(Image.open(w2_file), use_container_width=True)

        if w1_file and w2_file:
            if st.button("🔍 Compare Growth & Recovery Progress", type="primary", use_container_width=True):
                with st.spinner("Analyzing progress..."):
                    try:
                        i1 = Image.open(w1_file)
                        i2 = Image.open(w2_file)
                        i1.thumbnail((800, 800))
                        i2.thumbnail((800, 800))

                        comp_model = genai.GenerativeModel(model_name="gemini-flash")
                        prompt = "Compare these two plant images taken over consecutive weeks. Detail progress, leaf health recovery, growth changes, and actionable advice."

                        res = comp_model.generate_content([prompt, i1, i2])

                        st.success("Comparison Analysis Complete!")
                        st.markdown("### 📈 AI Recovery Analysis")
                        st.write(res.text)

                    except Exception as e:
                        st.error(f"Error running comparison: {e}")
