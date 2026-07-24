import os
import json
import base64
import requests
from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Plant Doctor Backend")

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Layout response validation schema matching your Pydantic tracking setup
class DiagnosisResponse(BaseModel):
    species: str
    condition: str
    confidence: str
    care_plan: List[str]

@app.get("/")
def home():
    return {"message": "Plant Doctor Backend is running successfully"}

@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_plant(file: UploadFile = File(...)):
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Corrected indentation block for token validation checkpoints
    if not api_key:
        return {
            "species": "Unknown Configuration",
            "condition": "OPENAI_API_KEY environment variable is completely missing.",
            "confidence": "0%",
            "care_plan": ["Go to your Hugging Face Space Settings page.", "Add your OpenAI token key as a Secret value."]
        }
        
    try:
        # Formulate clean byte storage buffers to handle images safely
        image_bytes = await file.read()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Explicit botany structure prompt matching your original criteria instructions
        botany_prompt = (
            "You are an expert botanist. Identify the exact plant species from the image. "
            "Then determine whether the plant is healthy or diseased. "
            "Respond ONLY as a valid JSON object matching this schema layout exactly: "
            '{"species": "string", "condition": "string", "confidence": "string", "care_plan": ["string", "string"]}'
        )
        
        payload = {
            "model": "gpt-4o-mini",
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": botany_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{file.content_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        # Executing unified REST payload checks to OpenAI models
        response = requests.post(
            "https://openai.com", 
            headers=headers, 
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            res_json = response.json()
            ai_response = res_json["choices"][0]["message"]["content"]
            data = json.loads(ai_response)
            return data
        else:
            return {
                "species": "OpenAI API Error Connection",
                "condition": f"Connection rejected with HTTP Status Code: {response.status_code}",
                "confidence": "0%",
                "care_plan": ["Verify your OpenAI platform balance account status.", f"Error description: {response.text[:100]}"]
            }
            
    except Exception as e:
        return {
            "species": "Backend Application Crash",
            "condition": f"Internal execution runtime failure: {str(e)}",
            "confidence": "0%",
            "care_plan": ["Check your image configuration types.", "Review deployment console output text logs."]
        }
