import os
import sys

# Ensure root directory is on sys.path for backend imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, File, UploadFile
from backend.agent import analyze_plant_image_with_openai

app = FastAPI(title="Plant Doctor Distributed Core Engine")

@app.get("/")
def read_root():
    return {"status": "online", "system": "Plant Doctor Core API"}

@app.post("/predict")
async def predict_plant_health(file: UploadFile = File(...)):
    try:
        incoming_payload_stream = await file.read()
        agent_diagnostic_matrix = analyze_plant_image_with_openai(incoming_payload_stream)
        return agent_diagnostic_matrix
    except Exception as server_crash_exception:
        return {
            "target_system_id": "Boundary Interface Operational Failure",
            "core_target_confidence": "0%",
            "treatment_plan": f"Exception cleared at entry gate: {str(server_crash_exception)}"
        }
