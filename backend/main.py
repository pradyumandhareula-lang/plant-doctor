import os
import json
import base64
import requests
import uvicorn

from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Plant Doctor Backend")

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


@app.get("/")
def home():
return {"message": "Plant Doctor Backend is running successfully."}


@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose_plant(file: UploadFile = File(...)):

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
return {
"species": "Unknown",
"condition": "OPENAI_API_KEY is missing.",
"confidence": "0%",
"care_plan": [
"Add your OPENAI_API_KEY in Hugging Face Secrets."
]
}

try:

image_bytes = await file.read()

base64_image = base64.b64encode(image_bytes).decode("utf-8")

headers = {
"Authorization": f"Bearer {api_key}",
"Content-Type": "application/json",
}

payload = {
"model": "gpt-4o-mini",
"messages": [
{
"role": "user",
"content": [
{
"type": "text",
"text": """
You are an expert botanist.

Identify the exact plant species from the image.

Then determine whether the plant is healthy or diseased.

Respond ONLY as valid JSON in this exact format:

{
"species": "...",
"condition": "...",
"confidence": "...",
"care_plan": [
"...",
"...",
"..."
]
}
"""
},
{
"type": "image_url",
"image_url": {
"url": f"data:image/jpeg;base64,{base64_image}"
},
},
],
}
],
"response_format": {
"type": "json_object"
},
"max_tokens": 500,
"temperature": 0.2
}

response = requests.post(
"https://api.openai.com/v1/chat/completions",
headers=headers,
json=payload,
timeout=60,
)

response.raise_for_status()

res_json = response.json()

ai_response = res_json["choices"][0]["message"]["content"]

data = json.loads(ai_response)

return {
"species": data.get("species", "Unknown"),
"condition": data.get("condition", "Healthy"),
"confidence": data.get("confidence", "Unknown"),
"care_plan": data.get(
"care_plan",
["Continue regular watering."]
),
}

except Exception as e:

return {
"species": "Unknown",
"condition": f"Error: {str(e)}",
"confidence": "0%",
"care_plan": [
"Check backend logs.",
"Verify OpenAI API key.",
"Try again."
],
}


if __name__ == "__main__":
uvicorn.run(app, host="0.0.0.0", port=7860)
