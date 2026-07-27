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

# Sidebar Navigation
st.sidebar.title("🌿 Plant Doctor AI")
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
            
        with col2:
            st.subheader("Results")
            if st.button("Run Botanical Analysis"):
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
    st.markdown("Have questions about plant care, watering schedules, or diseases? Chat with your AI assistant below!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your plant..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    model = genai.GenerativeModel("gemini-3.6-flash")
                    
                    formatted_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "model" if m["role"] == "assistant" else "user"
                        formatted_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=formatted_history)
                    response = chat.send_message(prompt)
                    ai_response = response.text
                    
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.error(f"Error generating response: {e}")
