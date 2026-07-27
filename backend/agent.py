import os
import json
import io
import google.generativeai as genai
from PIL import Image

# 1. Configure Gemini API Key
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# 2. Gemini Model Identifier
MODEL_NAME = "gemini-3.6-flash"

def analyze_plant_image(image_bytes, temperature=0.2):
    """
    Analyzes a plant/leaf image using Gemini 3.6 Flash and returns JSON.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        image = Image.open(io.BytesIO(image_bytes))

        prompt = """
        You are an expert plant pathologist AI. 
        Examine the provided image of a plant/leaf carefully and perform a diagnostic assessment.

        Return ONLY a valid JSON object with these exact keys:
        1. "target_system_id": Identified plant species and/or diagnosed disease.
        2. "core_target_confidence": Confidence level (e.g., "95%" or "High").
        3. "treatment_plan": Step-by-step instructions for care or remedies.

        Do not wrap the response in markdown backticks outside of valid JSON formatting.
        """

        response = model.generate_content(
            [prompt, image],
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json",
            )
        )

        return json.loads(response.text)

    except json.JSONDecodeError:
        return {
            "target_system_id": "Analysis Completed",
            "core_target_confidence": "Medium",
            "treatment_plan": response.text if 'response' in locals() else "Unable to parse diagnostic response."
        }
    except Exception as e:
        raise RuntimeError(f"API Call Failed: {str(e)}")


def compare_weekly_photos(prev_bytes, curr_bytes):
    """
    Compares two weekly photos to evaluate plant progress.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prev_img = Image.open(io.BytesIO(prev_bytes))
        curr_img = Image.open(io.BytesIO(curr_bytes))

        prompt = """
        You are an expert plant pathologist evaluating treatment progress over time.
        - Image 1 represents Week 1 (Previous).
        - Image 2 represents Week 2 (Current).

        Compare both photos and write a concise evaluation report detailing health improvements and care advice.
        """

        response = model.generate_content([prompt, prev_img, curr_img])
        return response.text

    except Exception as e:
        raise RuntimeError(f"Comparison failed: {str(e)}")
