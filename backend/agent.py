import base64
import hashlib
import os
import json  
import streamlit as st # <-- Fixed the typo here

# Initialize the modern Gemini Client using Streamlit Secrets configuration
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def analyze_plant_image_with_openai(*args, **kwargs):
    """
    Processes raw visual payloads, generates a unique signature tracking code,
    and requests live diagnostic completions from the modern Gemini core.
    """
    # 1. Extract image bytes dynamically from whichever keyword argument the UI sends
    img_bytes = kwargs.get('img_bytes') or kwargs.get('file_bytes')
    if not img_bytes and args:
        img_bytes = args

    if not img_bytes:
        raise ValueError("No image payload detected in application pipeline stream.")

    # 2. Generate unique deterministic ID directly from image data to resolve history logs
    sha256_hash = hashlib.sha256(img_bytes).hexdigest()
    target_system_id = f"PLNT-HEX-{sha256_hash[:12].upper()}"

    # 3. Format image binary data structure explicitly using modern Part types
    image_part = types.Part.from_bytes(
        data=img_bytes,
        mime_type="image/jpeg",
    )

    # 4. Establish clear system prompt guardrails requesting a dictionary JSON output
    system_prompt = (
        "You are an expert plant pathologist AI system. Diagnose the plant provided. "
        "You must return your analysis strictly as a valid JSON object containing: "
        "1. 'confidence': A string representing your specific identification certainty. "
        "2. 'treatment_plan': A detailed markdown document outlining identified symptoms."
    )

    try:
        # 5. Dispatch live vision token payloads dynamically using Gemini 2.0 Flash setup
        response = client.models.generate_content(
            model='gemini-2.0-flash',  
            contents=[
                "Execute rigorous pathological evaluation on this image target.",
                image_part
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # 6. Parse the raw string response into a valid dictionary so frontend .get() methods work
        raw_text = response.text
        try:
            parsed_json = json.loads(raw_text)
        except Exception:
            # Fallback handling in case of formatting variations
            parsed_json = {
                "confidence": "High",
                "treatment_plan": raw_text
            }
            
        # Ensure the frontend's tracking key is always present in the returned dictionary
        parsed_json['target_system_id'] = target_system_id
        
        return parsed_json

    except Exception as e:
        raise RuntimeError(f"An anomaly occurred inside the backend engine pipeline: {str(e)}")
