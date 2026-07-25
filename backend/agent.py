import os
import json
from PIL import Image
import io
from google import genai
from google.genai.types import HttpOptions

def analyze_plant_image(image_bytes: bytes) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    # Explicitly instruct the SDK to use the stable v1 API version
    client = genai.Client(
        api_key=api_key,
        http_options=HttpOptions(api_version="v1")
    )

    pil_img = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    You are an expert plant pathologist AI. Analyze the provided image and respond ONLY with a valid JSON object matching this schema:
    {
        "target_system_id": "Detected Plant Species / Name",
        "core_target_confidence": "Confidence level (e.g., 95%)",
        "treatment_plan": "A detailed markdown treatment plan and diagnosis."
    }
    """

    try:
        # gemini-2.5-flash runs on the free tier on v1
        response = client.models.generate_content(
            model='gemini-2.5-flash',
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
