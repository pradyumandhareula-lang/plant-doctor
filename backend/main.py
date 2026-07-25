import os
from backend.agent import analyze_plant_image_with_openai

def diagnose_plant(uploaded_file):
    """
    Main backend controller that processes the uploaded file and routes it
    to the advanced OpenAI Vision agent, with robust fallback logic.
    """
    try:
        # Read the uploaded file bytes
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0) # Reset pointer for safety
        
        # Invoke the advanced OpenAI Vision API via agent.py
        ai_analysis = analyze_plant_image_with_openai(file_bytes)
        
        return {
            "status": "Analysis Completed Successfully via OpenAI Vision",
            "label": ai_analysis.get("label", "Healthy / Unspecified"),
            "confidence": ai_analysis.get("confidence", 95),
            "treatment_plan": ai_analysis.get("treatment_plan", "No specific symptoms detected. Maintain regular watering.")
        }
        
    except Exception as error:
        # Robust Fallback Logic if OpenAI API fails, lacks credits, or times out
        return {
            "status": f"Fallback Mode Activated (Primary Service Offline: {str(error)})",
            "label": "General Plant Leaf Spot / Moisture Stress",
            "confidence": 70,
            "treatment_plan": (
                "1. Isolate the affected plant from healthy specimens immediately.\n"
                "2. Prune highly damaged or discolored leaves using sterilized tools.\n"
                "3. Optimize watering intervals—ensure the top two inches of soil dry completely.\n"
                "4. Technical Note: This advice is served via local fallback rules because the primary AI service is unreachable."
            )
        }
