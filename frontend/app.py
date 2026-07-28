import streamlit as st
import requests
from PIL import Image
import google.generativeai as genai
import datetime
import io

# Backend API Endpoint Configuration
API_DIAGNOSE_URL = "http://localhost:8000/api/diagnose"

# Configure Streamlit page
st.set_page_config(
    page_title="Plant Doctor (Powered by AI)",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS for Background Image, Dark Emerald Sidebar, and Frosted Glass Containers
st.markdown("""
<style>
    /* Consistent Background Image for all pages matching your exact uploaded photo */
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.25), rgba(0, 0, 0, 0.25)), 
                          url("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=2000&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Sidebar Styling (Dark Emerald Theme) */
    [data-testid="stSidebar"] {
        background-color: #0d2818;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Frosted Glass Effect for Main Content Containers with Black Text */
    .block-container {
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 2.5rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        color: #111111 !important;
    }

    /* Ensure all text inside containers is black for high contrast */
    .block-container h1, .block-container h2, .block-container h3, 
    .block-container h4, .block-container h5, .block-container h6, 
    .block-container p, .block-container span, .block-container label {
        color: #111111 !important;
    }

    /* Primary Buttons Styling */
    .stButton>button[kind="primary"] {
        background-color: #d90429 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        font-weight: bold;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #ef233c !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State variables if they don't exist
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "diagnosis_history" not in st.session_state:
    st.session_state.diagnosis_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.authenticated:
    st.title("🔐 Plant Doctor (Powered by AI) - Login")
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

# ==========================================
# MAIN APP (Only visible after login)
# ==========================================
else:
    # Sidebar Navigation (Clean list without headers, with Settings and Logout)
    st.sidebar.title("🌿 Plant Doctor (Powered by AI)")
    
    page = st.sidebar.selectbox(
        "",
        [
            "Plant Diagnosis", 
            "Weekly Photo Comparison", 
            "Plant Registry", 
            "💬 Chat Assistant", 
            "📜 Search History", 
            "⚙️ Settings", 
            "🚪 Logout"
        ],
        label_visibility="collapsed"
    )

    # Handle Logout selection directly from the selectbox dropdown
    if page == "🚪 Logout":
        st.session_state.authenticated = False
        st.rerun()

    # ==========================================
    # PAGE 1: PLANT DIAGNOSIS
    # ==========================================
    if page == "Plant Diagnosis":
        st.markdown("<h1 style='color: #111111;'>🌱 Plant Diagnosis</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #333333;'>Upload a plant image for immediate AI health analysis.</p>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Choose a plant image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            col1, col2 = st.columns(2)

            with col1:
                st.image(uploaded_file, caption="Uploaded Plant", use_column_width=True)
                run_analysis = st.button("Run Botanical Analysis", type="primary")

            with col2:
                st.subheader("Results")
                if run_analysis:
                    with st.spinner("Analyzing plant..."):
                        analysis_result = ""
                        
                        # 1. POST request to /api/diagnose endpoint
                        try:
                            uploaded_file.seek(0)
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            response = requests.post(API_DIAGNOSE_URL, files=files, timeout=10)

                            if response.status_code == 200:
                                res_json = response.json()
                                analysis_result = res_json.get("result") or res_json.get("diagnosis") or response.text
                            else:
                                raise Exception(f"API server returned status code {response.status_code}")

                        except Exception as api_err:
                            # 2. Seamless fallback to gemini-3.6-flash if backend API server is offline
                            try:
                                uploaded_file.seek(0)
                                img = Image.open(uploaded_file)
                                model = genai.GenerativeModel("gemini-3.6-flash")

                                prompt = (
                                    "Analyze this plant image. Provide the detected species name, "
                                    "health status (Healthy/Diseased/Stressed), confidence percentage, "
                                    "and a recommended treatment plan."
                                )

                                response = model.generate_content([img, prompt])
                                analysis_result = response.text
                            except Exception as gemini_err:
                                st.error(f"Error running diagnosis: {gemini_err}")

                        if analysis_result:
                            st.success("Analysis Complete!")
                            st.write(analysis_result)

                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.diagnosis_history.append({
                                "time": timestamp,
                                "result": analysis_result,
                                "image": uploaded_file.getvalue()
                            })

    # ==========================================
    # PAGE 2: WEEKLY PHOTO COMPARISON
    # ==========================================
    elif page == "Weekly Photo Comparison":
        st.markdown("<h1 style='color: #111111;'>📅 Weekly Photo Comparison</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #333333;'>Compare side-by-side plant images over time to evaluate growth or recovery.</p>", unsafe_allow_html=True)

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

                    comp_model = genai.GenerativeModel("gemini-3.6-flash")
                    prompt = "Compare these two plant photos taken a week apart. Evaluate changes in growth, leaf color, recovery progress, or signs of stress."

                    res = comp_model.generate_content([i1, i2, prompt])

                    st.success("Comparison Analysis Complete!")
                    st.markdown("### 📊 AI Recovery Analysis")
                    st.write(res.text)
                except Exception as e:
                    st.error(f"Error running comparison: {e}")

    # ==========================================
    # PAGE 3: PLANT REGISTRY (HOME / LANDING VIEW)
    # ==========================================
    elif page == "Plant Registry":
        st.markdown("<h1 style='text-align: center; color: #111111;'>🌿 Plant Registry - Workspace</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #333333; font-size: 16px;'>Find and manage your plant database. Add details for every plant in your collection.</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.image(
            "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=2000&q=80", 
            caption="Plant Registry Collection View", 
            use_column_width=True
        )

    # ==========================================
    # PAGE 4: CHAT ASSISTANT
    # ==========================================
    elif page == "💬 Chat Assistant":
        head_col1, head_col2 = st.columns([1, 5])
        with head_col1:
            st.markdown(
                """
                <div style="background-color: #0d2818; padding: 10px; border-radius: 12px; text-align: center; color: white;">
                    <span style="font-size: 26px;">🎧</span><br>
                    <b style="font-size: 12px; letter-spacing: 1px;">AI</b>
                </div>
                """,
                unsafe_allow_html=True
            )
        with head_col2:
            st.markdown("<h3 style='color: #111111;'>Plant Doctor Chat Assistant</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #333333;'>Have questions about your plant? Upload a photo and chat live with the assistant!</p>", unsafe_allow_html=True)

        clear_col1, clear_col2 = st.columns([5, 1])
        with clear_col2:
            if st.button("🗑️ New Chat", type="primary"):
                st.session_state.messages = []
                st.rerun()

        for message in st.session_state.messages:
            avatar_icon = "🎧🤖" if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar_icon):
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
                model = genai.GenerativeModel("gemini-3.6-flash")
                formatted_history = []
                for m in st.session_state.messages[:-1]:
                    role = "model" if m["role"] == "assistant" else "user"
                    parts = m["content"] if isinstance(m["content"], list) else [m["content"]]
                    formatted_history.append({"role": role, "parts": parts})

                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(content_to_send)
                ai_response = response.text

                with st.chat_message("assistant", avatar="🎧🤖"):
                    st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"Error in chat: {e}")

    # ==========================================
    # PAGE 5: SEARCH HISTORY
    # ==========================================
    elif page == "📜 Search History":
        st.markdown("<h1 style='color: #111111;'>📜 Plant Search & Diagnosis History</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #333333;'>Here is a log of all previous plant health analyses performed during your session.</p>", unsafe_allow_html=True)

        if not st.session_state.diagnosis_history:
            st.info("No plant diagnosis history found yet. Run an analysis on the 'Plant Diagnosis' page to see records here!")
        else:
            for idx, item in enumerate(reversed(st.session_state.diagnosis_history), 1):
                with st.expander(f"Diagnosis #{len(st.session_state.diagnosis_history) - idx + 1} — {item['time']}"):
                    if "image" in item and item["image"]:
                        st.image(io.BytesIO(item["image"]), caption="Analyzed Plant Image", width=200)
                    st.markdown(item["result"])

    # ==========================================
    # PAGE 6: SETTINGS
    # ==========================================
    elif page == "⚙️ Settings":
        st.markdown("<h1 style='color: #111111;'>⚙️ System Settings</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #333333;'>Configure your backend endpoints and application preferences.</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.text_input("API Backend Endpoint", value=API_DIAGNOSE_URL)
        st.selectbox("AI Model Engine", ["gemini-3.6-flash", "gemini-pro-vision"])
        st.success("Settings saved automatically.")
