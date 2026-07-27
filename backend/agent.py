import os
import json
import io
import google.generativeai as genai
from PIL import Image

# 1. Configure Gemini API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. Updated Model Identifier (gemini-2.5-flash)
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME)


def analyze_plant_image(image_bytes, temperature=0.2):
    """
    Analyzes a plant/leaf image and returns diagnostic findings as JSON.
    """
    try:
        # Convert raw bytes into a PIL Image for Gemini Vision
        image = Image.open(io.BytesIO(image_bytes))

        prompt = """
        You are an expert plant pathologist AI. 
        Examine the provided image of a plant/leaf carefully and perform a diagnostic assessment.

        Return ONLY a JSON object containing the exact following keys:
        1. "target_system_id": The identified plant species and/or diagnosed disease condition (e.g., "Tomato - Early Blight").
        2. "core_target_confidence": Confidence level of your diagnosis (e.g., "95%" or "High").
        3. "treatment_plan": Clear, step-by-step instructions for care, organic treatment, or chemical remedies.

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
        # Fallback if raw text returned instead of clean JSON
        return {
            "target_system_id": "Analysis Completed",
            "core_target_confidence": "Medium",
            "treatment_plan": response.text if 'response' in locals() else "Unable to parse diagnostic response."
        }
    except Exception as e:
        raise RuntimeError(f"API Call Failed: {str(e)}")


def compare_weekly_photos(prev_bytes, curr_bytes):
    """
    Compares two weekly photos to evaluate plant recovery or progress.
    """
    try:
        prev_img = Image.open(io.BytesIO(prev_bytes))
        curr_img = Image.open(io.BytesIO(curr_bytes))

        prompt = """
        You are an expert plant pathologist evaluating treatment progress over time.
        - Image 1 represents Week 1 (Previous).
        - Image 2 represents Week 2 (Current).

        Compare both photos and write a concise evaluation report:
        1. Visual health changes or leaf improvement.
        2. Status of pests, rot, or fungal spots (spread, reduced, or controlled).
        3. Clear recommendation on whether to continue or adjust current care.
        """

        response = model.generate_content([prompt, prev_img, curr_img])
        return response.text

    except Exception as e:
        raise RuntimeError(f"Comparison failed: {str(e)}")
