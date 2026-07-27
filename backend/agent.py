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


def analyze_plant_image(image_bytes: bytes = None, file_bytes: bytes = None, *args, temperature=0.2):
    data = image_bytes or file_bytes
    if data is None and args:
        data = args[0]
        
    api_key = get_gemini_api_key()
    if not api_key:
        # DO NOT return fake JSON data here — raise an exception so the frontend renders a true error state
        raise ValueError("GEMINI_API_KEY was not found in Streamlit secrets or Environment Variables.")

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        pil_img = Image.open(io.BytesIO(data))

        prompt = """You are an expert plant pathologist AI. Analyze the provided image and respond ONLY with a valid JSON object matching this structure:
{
  "target_system_id": "Detected Plant Species / Name",
  "core_target_confidence": "Confidence level (e.g., 95%)",
  "treatment_plan": "A detailed markdown treatment plan and diagnosis."
}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, pil_img],
            config=types.GenerateContentConfig(
                temperature=temperature
            )
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        return json.loads(raw_text.strip())

    except Exception as err:
        # Re-raise the exception so FastAPI/Streamlit handles it as a real error state
        raise RuntimeError(f"API Call Failed: {str(err)}") from err


def compare_weekly_photos(prev_bytes: bytes, curr_bytes: bytes):
    """
    Evaluates weekly plant progress comparing two uploaded images.
    Addresses evaluator requirements for photo progress tracking.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY was not found.")

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        prev_img = Image.open(io.BytesIO(prev_bytes))
        curr_img = Image.open(io.BytesIO(curr_bytes))

        prompt = """You are an expert plant pathologist evaluating a plant's progress over time.
Image 1 is from a previous check-in.
Image 2 is from the current check-in.

Compare both images and provide a progress report answering:
1. Has the plant's condition improved, deteriorated, or remained the same?
2. What visible changes occurred (e.g., leaf discoloration, new growth, wilting)?
3. What adjustments should be made to the current treatment plan?
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, prev_img, curr_img]
        )

        return response.text

    except Exception as err:
        raise RuntimeError(f"Photo comparison failed: {str(err)}") from err


# Backwards compatibility aliases
analyze_plant_image_with_openai = analyze_plant_image
analyze_plant_image_with_gemini = analyze_plant_image
