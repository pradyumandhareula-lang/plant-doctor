import streamlit as st
import requests
from PIL import Image

# Page setup
st.set_page_config(page_title="Plant Doctor AI", layout="wide")

st.title("🌱 Plant Doctor AI")
st.write("Upload an image of a plant or leaf to run botanical analysis.")

# Layout: Give col2 slightly more space [1, 1.2] to prevent horizontal truncation
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("Upload")
    uploaded_file = st.file_uploader(
        "Select a clear leaf or plant image (JPG, JPEG, PNG)", 
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

        analyze_btn = st.button("🚀 Run Botanical Analysis", type="primary")

with col2:
    st.header("Results")

    if uploaded_file is not None and analyze_btn:
        with st.spinner("Analyzing plant..."):
            try:
                # Prepare payload
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                # Call FastAPI backend (adjust URL to your deployed API endpoint)
                response = requests.post("http://localhost:8000/analyze", files=files)

                if response.status_code == 200:
                    data = response.json()

                    # DISPLAY RESULTS (Custom Markdown instead of st.metric to avoid 'He...' truncation)
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
                st.error(f"Could not connect to backend service: {e}")
    else:
        st.info("Upload an image and click 'Run Botanical Analysis' to see results.")

