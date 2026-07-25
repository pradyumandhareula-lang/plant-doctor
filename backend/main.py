import os
import re
from fastapi import FastAPI, File, UploadFile
from backend.agent import analyze_plant_image_with_openai

app = FastAPI(title="Plant Doctor Distributed Core Engine")

@app.post("/predict")
async def predict_plant_health(file: UploadFile = File(...)):
    """
    Core FastAPI boundary layer parsing byte payloads downstream 
    into the LangGraph evaluation state loops.
    """
    try:
        incoming_payload_stream = await file.read()
        agent_diagnostic_matrix = analyze_plant_image_with_openai(incoming_payload_stream)
        return agent_diagnostic_matrix
    except Exception as server_crash_exception:
        return {
            "status": "System Fault Routed",
            "label": "Boundary Interface Operational Failure",
            "confidence": 0,
            "treatment_plan": f"Exception cleared at entry gate: {str(server_crash_exception)}"
        }
