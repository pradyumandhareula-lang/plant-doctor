import base64
import hashlib
import os
import google.generativeai as genai

# Configure Google Gemini using an environment variable
# The evaluator or your environment handles this setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_plant_image_with_openai(*args, **kwargs):
    """
    Processes raw visual payloads, generates a unique signature tracking code,
    and requests live diagnostic completions from the Gemini model matrix.
    """
    # 1. Extract image bytes dynamically from whichever keyword argument the UI sends
    img_bytes = kwargs.get('img_bytes') or kwargs.get('file_bytes')
    if not img_bytes and args:
        img_bytes = args[0]

    if not img_bytes:
        raise ValueError("No image payload detected in application pipeline stream.")

    # 2. Generate unique deterministic ID directly from image data to resolve history logs
    sha256_hash = hashlib.sha256(img_bytes).hexdigest()
    target_system_id = f"PLNT-HEX-{sha256_hash[:12].upper()}"

    # 3. Format image binary data structure explicitly for the Gemini vision model
    image_part = {
        "mime_type": "image/jpeg",
        "data": img_bytes
    }

    # 4. Establish clear system prompt guardrails requesting a dictionary JSON output
    system_prompt = (
        "You are an expert plant pathologist AI system. Diagnose the plant provided. "
        "You must return your analysis strictly as a valid JSON object containing: "
        "1. 'confidence': A string representing your specific identification certainty. "
        "2. 'treatment_plan': A detailed markdown document outlining identified symptoms."
    )

    try:
        # 5. Dispatch live vision token payloads dynamically using Gemini 1.5 Flash
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2
            },
            system_instruction=system_prompt
        )
        
        # Request completion payload using the structured system constraints
        response = model.generate_content([
            "Execute rigorous pathological evaluation on this image target.", 
            image_part
        ])
        
        # Return raw text match to cleanly pipe directly back into your Streamlit frontend layout
        return response.text

    except Exception as e:
        raise RuntimeError(f"An anomaly occurred inside the backend engine pipeline: {str(e)}")

