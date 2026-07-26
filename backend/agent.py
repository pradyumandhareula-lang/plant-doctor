import os
import json
import io
from PIL import Image

def get_gemini_api_key():
    # 1. Try reading directly from Streamlit secrets
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # 2. Try OS environment variable
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

def analyze_plant_image(image_bytes: bytes = None, file_bytes: bytes = None, temperature: float = 0.2, *args, **kwargs) -> dict:
    data = image_bytes or file_bytes
    if data is None and args:
        data = args[0]
        
    api_key = get_gemini_api_key()
    
    if api_key:
        try:
            from google import genai
            from google.genai import types

            # Pass api_key explicitly to the client
            client = genai.Client(api_key=api_key)
            pil_img = Image.open(io.BytesIO(data))

            prompt = """
You are an expert plant pathologist AI. Analyze the provided image and respond ONLY with a valid JSON object matching this structure:
{
  "target_system_id": "Detected Plant Species / Name",
  "core_target_confidence": "Confidence level (e.g., 95%)",
  "treatment_plan": "A detailed markdown treatment plan and diagnosis."
}
"""

            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[prompt, pil_img],
                config=types.GenerateContentConfig(
                    temperature=temperature
                )
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            return json.loads(raw_text.strip())

        except Exception as err:
            # Output actual error in the UI so you can see why the live API call failed
            return {
                "target_system_id": "API Analysis Error",
                "core_target_confidence": "0%",
                "treatment_plan": f"**API Call Failed:** {str(err)}"
            }

    return {
        "target_system_id": "API Key Missing",
        "core_target_confidence": "0%",
        "treatment_plan": "GEMINI_API_KEY was not found in Streamlit secrets or Environment Variables."
    }

analyze_plant_image_with_openai = analyze_plant_image
analyze_plant_image_with_gemini = analyze_plant_image
