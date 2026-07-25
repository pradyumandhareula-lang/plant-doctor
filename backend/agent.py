import os
import json
import io
from PIL import Image
from google import genai
from google.genai import types

def get_gemini_api_key():
    """Retrieves API key from OS environment or Streamlit secrets safely."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return None

def analyze_plant_image(image_bytes: bytes = None, file_bytes: bytes = None, *args, **kwargs) -> dict:
    data = image_bytes or file_bytes
    if data is None and args:
        data = args[0]

    api_key = get_gemini_api_key()
    if not api_key:
        return {
            "target_system_id": "API Key Missing",
            "core_target_confidence": "0%",
            "treatment_plan": "GEMINI_API_KEY is not configured in Environment Variables or Streamlit Secrets."
        }

    # Remove api_version='v1' so the client resolves standard model endpoints automatically
    client = genai.Client(api_key=api_key)

    pil_img = Image.open(io.BytesIO(data))
    
    prompt = """
    You are an expert plant pathologist AI. Analyze the provided image and respond ONLY with a valid JSON object matching this schema:
    {
        "target_system_id": "Detected Plant Species / Name",
        "core_target_confidence": "Confidence level (e.g., 95%)",
        "treatment_plan": "A detailed markdown treatment plan and diagnosis."
    }
    """

    try:
        # gemini-2.0-flash is the standard active model endpoint
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, pil_img]
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        return json.loads(raw_text.strip())

    except Exception as e:
        return {
            "target_system_id": "Error",
            "core_target_confidence": "0%",
            "treatment_plan": f"Vision analysis fault: {str(e)}"
        }

# Aliases so any import name works seamlessly
analyze_plant_image_with_openai = analyze_plant_image
analyze_plant_image_with_gemini = analyze_plant_image
