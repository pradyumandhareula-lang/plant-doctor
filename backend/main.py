import io
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import google.generativeai as genai

app = FastAPI()

# Configure your Gemini API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY")

SYSTEM_PROMPT = """
You are an expert botanical doctor AI. Analyze the uploaded plant image and identify:
1. Plant species (common and scientific name). If no plant/flower/leaf is present, set species to 'Unknown'.
2. Health status and confidence percentage (0-100%).
3. Recommended treatment plan (bullet points for Sunlight, Watering, and Care).

Respond strictly in valid JSON format matching this schema:
{
    "species": "Plant Name",
    "health_status": "Healthy / Diseased",
    "confidence": 95,
    "treatment_plan": [
        "Sunlight: ...",
        "Watering: ...",
        "Care: ..."
    ]
}
"""

@app.post("/api/diagnose")
async def analyze_plant(file: UploadFile = File(...)):
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # COMPRESSION STEP: Resize image to speed up API processing time
        image.thumbnail((800, 800))

        # Use gemini-3.6-flash for maximum speed and accuracy on vision tasks
        model = genai.GenerativeModel(
            model_name="gemini-3.6-flash",
            system_instruction=SYSTEM_PROMPT
        )

        # Generate response with structured JSON output
        response = model.generate_content(
            [image, "Analyze this plant image."],
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2 # Lower temperature = faster, consistent accuracy
            }
        )

        # Parse JSON response
        result_data = json.loads(response.text)
        return result_data

    except Exception as e:
    raise HTTPException(status_code=500, detail={"error": True, "message": str(e)})
