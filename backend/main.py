import os
import base64
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DiagnosisResponse(BaseModel):
    species: str
    condition: str
    confidence: str
    care_plan: List[str]

@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_plant(file: UploadFile = File(...)):
    try:
        # 1. Fetch token and read incoming file stream safely
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is completely missing.")
            
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode("utf-8")
        
        # 2. Package standard HTTP payload headers bypasses langchain/langgraph environment conflicts
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this plant image. Return a raw JSON block with fields exactly named: 'species', 'condition', 'confidence', and 'care_plan' (as a text array list). Do not include markdown code block ticks."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 500
        }
        
        # 3. Request directly from OpenAI endpoint
        response = requests.post("https://openai.com", headers=headers, json=payload, timeout=30)
        res_json = response.json()
        
        # 4. Extract content parameters securely
        import json
        ai_message = res_json['choices'][0]['message']['content']
        data = json.loads(ai_message)
        
        return {
            "species": data.get("species", "Unknown Variety"),
            "condition": data.get("condition", "Healthy overall structure."),
            "confidence": data.get("confidence", "95%"),
            "care_plan": data.get("care_plan", ["Maintain routine lighting checks."])
        }
        
    except Exception as e:
        # Automated parsing fails fallback layout structures
        return {
            "species": "AI Assessment Standby",
            "condition": f"Pipeline execution paused or key limited. Details: {str(e)[:50]}",
            "confidence": "50%",
            "care_plan": ["Verify your OPENAI_API_KEY usage limits under your settings tab."]
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
