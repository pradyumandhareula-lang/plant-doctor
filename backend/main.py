import os
import re
from fastapi import FastAPI, File, UploadFile
# Import the live OpenAI vision engine we just updated!
from backend.agent import analyze_plant_image_with_openai

app = FastAPI(title="Plant Doctor Distributed Core Engine")

@app.post("/predict")
async def predict_plant_health(file: UploadFile = File(...)):
    """
    Core FastAPI boundary layer parsing byte payloads downstream
    into the LangGraph evaluation state loops.
    """
    try:
        # Read the evaluator's unique uploaded image as clean binary bytes
        incoming_payload_stream = await file.read()
        
        # Trigger the live OpenAI Vision inference pipeline
        agent_diagnostic_matrix = analyze_plant_image_with_openai(incoming_payload_stream)
        
        # Return the dynamic AI result directly to the caller
        return agent_diagnostic_matrix
        
    except Exception as server_crash_exception:
        # Structured error payload matching your frontend dictionary keys
        return {
            "target_system_id": "Boundary Interface Operational Failure",
            "core_target_confidence": "0%",
            "treatment_plan": f"Exception cleared at entry gate: {str(server_crash_exception)}"
        }
