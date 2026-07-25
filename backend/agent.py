import base64
import hashlib
import os
import json
import streamlit as st
from google import genai
from google.genai import types

def analyze_plant_image_with_openai(*args, **kwargs):
    """
    Processes raw visual payloads, generates a unique signature tracking code,
    and requests live diagnostic completions from the modern Gemini core.
    """
    # 1. API Key retrieval (Checks kwargs, os.environ, and Streamlit secrets)
    api_key = kwargs.get('api_key') or os.environ.get("GEMINI_API_KEY")
    if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]

    if not api_key:
        raise ValueError("API key is missing. Please provide a valid Gemini API Key.")

    # 2. Extract image bytes dynamically from kwargs or positional args
    img_bytes = kwargs.get('img_bytes') or kwargs.get('file_bytes')
    if not img_bytes and args:
        img_bytes = args[0]

    if not img_bytes:
        raise ValueError("No image payload detected in application pipeline stream.")

    # Extract dynamic temperature or default to 0.2
    temperature = kwargs.get('temperature', 0.2)

    # 3. Initialize the Google GenAI client safely per request
    client = genai.Client(api_key=api_key)

    # 4. Generate unique deterministic ID directly from image data
    sha256_hash = hashlib.sha256(img_bytes).hexdigest()
    target_system_id = f"PLNT-HEX-{sha256_hash[:12].upper()}"

    # 5. Format image binary data structure explicitly using modern Part types
    image_part = types.Part.from_bytes(
        data=img_bytes,
        mime_type="image/jpeg"
    )

    # 6. Establish clear system prompt guardrails requesting a dictionary JSON output
    system_prompt = (
        "You are an expert plant pathologist AI system. Diagnose the plant provided in the image. "
        "You must return your analysis strictly as a valid JSON object containing: "
        "1. 'target_system_id': A string or plant name identified, "
        "2. 'core_target_confidence': A string confidence score (e.g., '94%'), "
        "3. 'treatment_plan': A detailed markdown document outlining identified symptoms, diagnosis, and steps to treat the plant."
    )

    try:
        # 7. Dispatch live vision token payloads dynamically using Gemini 2.0 Flash
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                "Execute rigorous pathological evaluation on this image target.",
                image_part
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                response_mime_type="application/json"
            )
        )

        # 8. Parse the raw string response into a valid dictionary
        raw_text = response.text
        try:
            parsed_json = json.loads(raw_text)
        except Exception:
            # Fallback handling in case of formatting variations
            parsed_json = {
                "core_target_confidence": "High",
                "treatment_plan": raw_text
            }

        # Ensure the tracking keys exist in the returned dictionary
        if "target_system_id" not in parsed_json:
            parsed_json["target_system_id"] = target_system_id

        return parsed_json

    except Exception as e:
        raise RuntimeError(f"An anomaly occurred inside the backend engine pipeline: {str(e)}")
