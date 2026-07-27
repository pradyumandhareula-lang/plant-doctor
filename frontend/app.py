import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="Plant Doctor AI",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS styling for full green theme, black text, red buttons, and compact sidebar logout
st.markdown("""
<style>
    /* Full green background for the entire app, main containers, and Streamlit header toolbar */
    .stApp, [data-testid="stSidebar"], [data-testid="stMain"], [data-testid="block-container"], header[data-testid="stHeader"] {
        background-color: #2e7d32 !important;
    }
    
    /* Make the selectbox container in the sidebar white with black text */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    [data-testid="stSidebar"] .stSelectbox span {
        color: #000000 !important;
    }
    
    /* Make all headings, markdown text, and labels black */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stSubheader, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] span {
        color: #000000 !important;
    }
    
    /* Primary / action buttons styled in RED */
    div.stButton > button, div.stButton > button[kind="primary"] {
        background-color: #d32f2f !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover, div.stButton > button[kind="primary"]:hover {
        background-color: #b71c1c !important;
        color: white !important;
    }
    
    /* File uploader custom styling: compact size, green background, white border, black text */
    [data-testid="stFileUploader"] {
        max-width: 400px !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #2e7d32 !important;
        border: 2px solid #ffffff !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #000000 !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #d32f2f !important;
        color: #ffffff !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "diagnosis_history" not in st.session_state:
    st.session_state.diagnosis_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "registered_plants" not in st.session_state:
    st.session_state.registered_plants = []


# ============================================
# LOGIN PAGE
# ============================================
if not st.session_state.authenticated:
    st.title("🔐 Plant Doctor AI - Login")
    st.markdown("Please log in with your credentials to access the plant doctor system.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In", type="primary")

        if submit_button:
            if username == "admin" and password == "password123":
                st.session_state.authenticated = True
                st.success("Login successful! Loading app...")
                st.rerun()
            else:
                st.error("Invalid username or password. Try username: admin, password: password123")

# ============================================
# MAIN APP (Only visible after login)
# ============================================
else:
    # Sidebar Navigation & Clean Logout Button
    st.sidebar.title("🌿 Navigation")

    page = st.sidebar.selectbox(
        "Select Feature",
        ["Plant Diagnosis", "Weekly Photo Comparison", "Plant Registry", "💬 Chat Assistant", "📜 Search History"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Account")
    if st.sidebar.button("🚪 Logout", type="primary"):
        st.session_state.authenticated = False
        st.rerun()

    # Clean centered Title in the main area
    st.markdown("<h1 style='text-align: center; font-size: 2.8rem;'>🌿 Plant Doctor AI</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # ============================================
    # PAGE 1: PLANT DIAGNOSIS
    # ============================================
    if page == "Plant Diagnosis":
        st.markdown("### 🌿 Plant Health Diagnosis")
        st.markdown("Upload a plant image for immediate AI health analysis.")

        uploaded_file = st.file_uploader("Choose a plant image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            plant_registry = st.text_input("Plant Registry ID / Name", placeholder="e.g., REG-001")
            
            col1, col2 = st.columns(2)

            with col1:
                st.image(uploaded_file, caption="Uploaded Plant", use_column_width=True)
                run_analysis = st.button("Run Botanical Analysis", type="primary")

            with col2:
                st.subheader("Results")
                if run_analysis:
                    with st.spinner("Analyzing plant..."):
                        try:
                            img = Image.open(uploaded_file)
                            model = genai.GenerativeModel("gemini-3.6")

                            prompt = (
                                "Analyze this plant image. Provide the detected species name, "
                                "health status (Healthy/Diseased/Stressed), confidence percentage, "
                                "and a recommended treatment plan."
                            )

                            response = model.generate_content([img, prompt])
                            analysis_result = response.text

                            st.success("Analysis Complete!")
                            st.markdown(analysis_result)

                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            st.session_state.diagnosis_history.append({
                                "time": timestamp,
                                "plantregistry": plant_registry if plant_registry else "Unregistered",
                                "result": analysis_result
                            })

                        except Exception as e:
                            st.error(f"Error running diagnosis: {e}")

    # ============================================
    # PAGE 2: WEEKLY PHOTO COMPARISON
    # ============================================
    elif page == "Weekly Photo Comparison":
        st.markdown("### 📅 Weekly Photo Comparison")
        st.markdown("Compare side-by-side plant images over time to evaluate growth or recovery.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Week 1 (Baseline)")
            w1_file = st.file_uploader("Upload Week 1 Photo", type=["jpg", "jpeg", "png"], key="w1")
            if w1_file:
                st.image(w1_file, use_column_width=True)

        with col2:
            st.subheader("Week 2 (Current)")
            w2_file = st.file_uploader("Upload Week 2 Photo", type=["jpg", "jpeg", "png"], key="w2")
            if w2_file:
                st.image(w2_file, use_column_width=True)

        if w1_file and w2_file:
            if st.button("🔍 Compare Growth & Recovery Progress", type="primary"):
                try:
                    i1 = Image.open(w1_file)
                    i2 = Image.open(w2_file)
                    i1.thumbnail((800, 800))
                    i2.thumbnail((800, 800))

                    comp_model = genai.GenerativeModel("gemini-3.6")
                    prompt = "Compare these two plant photos taken a week apart. Evaluate changes in growth, leaf color, recovery progress, or signs of stress."

                    res = comp_model.generate_content([i1, i2, prompt])

                    st.success("Comparison Analysis Complete!")
                    st.markdown("### 📊 AI Recovery Analysis")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"Error running comparison: {e}")

    # ============================================
    # PAGE 3: PLANT REGISTRY TAB
    # ============================================
    elif page == "Plant Registry":
        st.markdown("### 🌿 Plant Registry Management")
        st.markdown("Manage and view your registered plants and their history.")
        
        with st.form("registry_form"):
            reg_id = st.text_input("Plant Registry ID (e.g., REG-001)")
            plant_name = st.text_input("Plant Name / Species (e.g., Alocasia or Ficus lyrata)")
            location = st.text_input("Location (e.g., Living Room, Balcony)")
            submitted = st.form_submit_button("Register Plant", type="primary")
            
            if submitted:
                if reg_id and plant_name:
                    st.session_state.registered_plants.append({
                        "registry_id": reg_id,
                        "name": plant_name,
                        "location": location,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success(f"Successfully registered {plant_name} under ID: {reg_id}!")
                else:
                    st.error("Please provide both a Registry ID and a Plant Name.")

        st.markdown("---")
        st.subheader("📋 Current Registered Plants")
        
        if not st.session_state.registered_plants:
            st.info("No plants registered yet.")
        else:
            for p in st.session_state.registered_plants:
                with st.expander(f"{p['registry_id']} — {p['name']}"):
                    st.write(f"**Location:** {p['location']}")
                    st.write(f"**Registration Date:** {p['date']}")

    # ============================================
    # PAGE 4: CHAT ASSISTANT
    # ============================================
    elif page == "💬 Chat Assistant":
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            st.markdown("### 💬 Plant Doctor Chat Assistant")
            st.markdown("Have questions about your plant? Upload a photo and type your question below!")
        with chat_col2:
            if st.button("🗑️ New Chat", type="primary"):
                st.session_state.messages = []
                st.rerun()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if isinstance(message["content"], list):
                    for item in message["content"]:
                        if isinstance(item, Image.Image):
                            st.image(item, width=250)
                        else:
                            st.markdown(item)
                else:
                    st.markdown(message["content"])

        st.markdown("---")
        st.subheader("📷 Attach Photo for Chat Query")
        chat_image = st.file_uploader("Upload a plant photo for the assistant to inspect", type=["jpg", "jpeg", "png"], key="chat_uploader")

        if chat_image:
            st.image(chat_image, caption="Attached Photo Preview", width=200)

        if prompt := st.chat_input("Ask a question about the photo or your plant care..."):
            content_to_send = [prompt]
            display_content = [prompt]

            if chat_image:
                img_obj = Image.open(chat_image)
                content_to_send.append(img_obj)
                display_content.append(img_obj)

            st.session_state.messages.append({"role": "user", "content": display_content})
            with st.chat_message("user"):
                st.markdown(prompt)
                if chat_image:
                    st.image(chat_image, width=200)

            try:
                model = genai.GenerativeModel("gemini-3.6")
                
                formatted_history = []
                for m in st.session_state.messages[:-1]:
                    role = "model" if m["role"] == "assistant" else "user"
                    parts = m["content"] if isinstance(m["content"], list) else [m["content"]]
                    formatted_history.append({"role": role, "parts": parts})

                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(content_to_send)
                ai_response = response.text

                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"Error in chat assistant: {e}")

    # ============================================
    # PAGE 5: SEARCH HISTORY
    # ============================================
    elif page == "📜 Search History":
        st.markdown("### 📜 Plant Search & Diagnosis History")
        st.markdown("Here is a log of all previous plant health analyses performed during your session.")

        if not st.session_state.diagnosis_history:
            st.info("No plant diagnosis history found yet. Run an analysis on the 'Plant Diagnosis' page to see records here!")
        else:
            for idx, item in enumerate(reversed(st.session_state.diagnosis_history), 1):
                reg_id = item.get("plantregistry", "Unregistered")
                timestamp = item.get("time", "")
                
                with st.expander(f"Registry: {reg_id} — {timestamp}"):
                    st.markdown(item["result"])
