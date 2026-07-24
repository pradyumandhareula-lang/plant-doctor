import os
import base64
import json
import requests
import uvicorn

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

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

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
raise HTTPException(
status_code=500,
detail="OPENAI_API_KEY environment variable not found."
)

if not file.content_type.startswith("image/"):
raise HTTPException(
status_code=400,
detail="Please upload an image file."
)

contents = await file.read()

base64_image = base64.b64encode(contents).decode("utf-8")

headers = {
"Authorization": f"Bearer {api_key}",
"Content-Type": "application/json"
}

prompt = """
You are an expert botanist and plant pathologist.

Carefully inspect the uploaded image.

Identify:

1. Exact plant species.
2. Whether the plant is healthy or diseased.
3. If diseased, identify the disease.
4. Give a realistic confidence percentage.
5. Give 4 practical care steps.

If uncertain, return the closest possible species.

Return ONLY valid JSON exactly like this:

{
"species":"",
"condition":"",
"confidence":"",
"care_plan":[]
}

Never return markdown.
"""

payload = {
"model": "gpt-4o-mini",
"messages": [
{
"role": "user",
"content": [
{
"type": "text",
"text": prompt
},
{
"type": "image_url",
"image_url": {
"url": f"data:image/jpeg;base64,{base64_image}"
}
}
]
}
],
"response_format": {
"type": "json_object"
},
"max_tokens": 500
}

try:

response = requests.post(
"https://api.openai.com/v1/chat/completions",
headers=headers,
json=payload,
timeout=60,
)

response.raise_for_status()

res_json = response.json()

ai_message = res_json["choices"][0]["message"]["content"]

data = json.loads(ai_message)

return DiagnosisResponse(
species=data.get("species", "Unknown Plant"),
condition=data.get("condition", "Unable to determine"),
confidence=data.get("confidence", "Unknown"),
care_plan=data.get(
"care_plan",
[
"Provide adequate sunlight.",
"Water appropriately.",
"Monitor leaves regularly.",
"Use balanced fertilizer."
]
)
)

except Exception as e:

raise HTTPException(
status_code=500,
detail=f"Diagnosis failed: {str(e)}"
)


if __name__ == "__main__":
uvicorn.run(app, host="0.0.0.0", port=7860)
