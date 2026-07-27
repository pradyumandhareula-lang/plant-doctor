import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# Configure page settings
st.set_page_config(
    page_title="Plant Doctor AI",
    page_icon="🌿",
    layout="wide"
)

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ==========================================
# LOGIN PAGE
# ==========================================
if not st.session_state.authenticated:
    st.title("🔐 Plant Doctor AI - Login")
    st.markdown("Please log in with your credentials to access the plant doctor system.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")

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
    # Sidebar Navigation
    st.sidebar.title("🌿 Plant Doctor AI")
    
    if st.sidebar.button("Log Out"):
        st.session_state.authenticated = False
        st.rerun()

    page = st.sidebar.selectbox(
        "Select Feature", 
        ["Plant Diagnosis", "Weekly Photo Comparison", "💬 Chat Assistant"]
    )

    # ==========================================
    # PAGE 1: PLANT DIAGNOSIS
    # ==========================================
    if page == "Plant Diagnosis":
        st.title("🌱 Plant Health Diagnosis")
        st.markdown("Upload a plant image for immediate AI health analysis.")

        uploaded_file = st.file_uploader("Choose a plant image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(uploaded_file, caption="Uploaded Plant", use_column_width=True)
                run_analysis = st.button("Run Botanical Analysis")
                
            with col2:
                st.subheader("Results")
                if run_analysis:
                    with st.spinner("Analyzing plant..."):
                        try:
                            img = Image.open(uploaded_file)
                            model = genai.GenerativeModel("gemini-3.6-flash")
                            
                            prompt = (
                                "Analyze this plant image. Provide the detected species name, "
                                "health status (Healthy/Diseased/Stressed), confidence percentage, "
                                "and a recommended treatment plan."
                            )
                            
                            response = model.generate_content([img, prompt])
                            st.success("Analysis Complete!")
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"Error running diagnosis: {e}")

    # ==========================================
    # PAGE 2: WEEKLY PHOTO COMPARISON
    # ==========================================
    elif page == "Weekly Photo Comparison":
        st.title("📅 Weekly Photo Comparison")
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
            if st.button("🔍 Compare Growth & Recovery Progress"):
                with st.spinner("Analyzing progress..."):
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
    # PAGE 3: CHAT ASSISTANT
    # ==========================================
    elif page == "💬 Chat Assistant":
        st.title("💬 Plant Doctor Chat Assistant")
        st.markdown("Have questions about your plant? **Please upload a photo below** and type your question to get AI-powered answers about the image!")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
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

        # Dedicated column/uploader block inside the chat interface
        st.markdown("---")
        st.subheader("📷 Attach Photo for Chat Query")
        chat_image = st.file_uploader("Upload a plant photo for the assistant to inspect", type=["jpg", "jpeg", "png"], key="chat_uploader")
        
        if chat_image:
            st.image(chat_image, caption="Attached Photo Preview", width=200)

        # Chat text input
        if prompt := st.chat_input("Ask a question about the photo or your plant care..."):
            # Construct content payload
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
                    st.image(chat_image, width=250)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing your photo and question..."):
                    try:
                        model = genai.GenerativeModel("gemini-3.6-flash")
                        
                        # Rebuild history securely for the model
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
                        st.error(f"Error generating response: {e}")
