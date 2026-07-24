import streamlit as st
import requests

st.set_page_config(
page_title="Plant Doctor Suite",
page_icon="🌿",
layout="wide"
)

st.title("🌿 AI Plant Doctor")
st.write("Upload a photo of any plant to generate an instant AI diagnostic report.")

tab1, tab2, tab3 = st.tabs(
["🔍 New Scan", "📜 Scan History", "📅 Care Reminder"]
)

with tab1:

uploaded_file = st.file_uploader(
"Choose a plant photo...",
type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

st.image(
uploaded_file,
caption="Uploaded Plant",
use_container_width=True
)

if st.button("Run Plant Diagnosis 🩺"):

with st.spinner("Analyzing plant..."):

backend_url = "https://pradyuman-dhareula-plant-doctor-backend.hf.space/diagnose"

try:

files = {
"file": (
uploaded_file.name,
uploaded_file.getvalue(),
uploaded_file.type
)
}

response = requests.post(
backend_url,
files=files,
timeout=90
)

if response.status_code == 200:

result = response.json()

st.success("Analysis Complete!")

st.subheader("🌱 Plant Species")
st.write(result.get("species", "Unknown"))

st.subheader("🍃 Plant Condition")
st.write(result.get("condition", "Unknown"))

st.subheader("📊 Confidence")
st.write(result.get("confidence", "Unknown"))

st.subheader("✅ Care Plan")

for step in result.get("care_plan", []):
st.write(f"• {step}")

else:
st.error(f"Backend Error: {response.status_code}")
st.write(response.text)

except Exception as e:
st.error(f"Connection failed: {e}")

with tab2:
st.info("📜 Scan history feature coming soon.")

with tab3:
st.info("📅 Care reminder feature coming soon.")
