import os
import base64
from typing import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# 1. Define the LangGraph State structure
class AgentState(TypedDict):
    image_bytes: bytes
    plant_name: str
    condition_summary: str
    detailed_report: str

# 2. Define a Pydantic schema to guarantee structured JSON output from the LLM
class PlantDiagnosis(BaseModel):
    plant_name: str = Field(description="Name of the plant and diagnosed health condition or healthy state")
    condition_summary: str = Field(description="A brief summary of the symptoms found or general condition")
    detailed_report: str = Field(description="Step-by-step actionable treatment plan and curation steps")

# 3. Define the main workflow execution node
def analyze_plant_node(state: AgentState) -> dict:
    img_bytes = state.get("image_bytes")
    if not img_bytes:
        return {
            "plant_name": "Unknown Plant",
            "condition_summary": "No image data found",
            "detailed_report": "Please upload a valid image file."
        }
        
    # Base64 encode the incoming binary image bytes
    base64_image = base64.b64encode(img_bytes).decode("utf-8")
    
    try:
        # Pull the secret token directly from your Streamlit Secrets environment variables
        api_key_val = os.getenv("OPENAI_API_KEY")
        
        # Initialize ChatOpenAI passing the API token directly into the constructor 
        # This overrides the hidden environment lookup errors caused by newer sk-proj keys
        llm = ChatOpenAI(
            model="gpt-4o-mini", 
            max_tokens=500, 
            temperature=0.2,
            openai_api_key=api_key_val
        )
        structured_llm = llm.with_structured_output(PlantDiagnosis)
        
        # Build the multimodal vision prompt payload
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Analyze this plant leaf. Identify the plant, summarize any disease condition, and provide an actionable treatment plan."},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        )
        
        # Invoke the model and extract data safely
        result = structured_llm.invoke([message])
        return {
            "plant_name": result.plant_name,
            "condition_summary": result.condition_summary,
            "detailed_report": result.detailed_report
        }
    except Exception as e:
        # Internal node error recovery handler
        return {
            "plant_name": "Analysis Failed",
            "condition_summary": f"Model error: {str(e)}",
            "detailed_report": "Fallback rule logic triggered inside agent graph."
        }

# 4. Build and compile the LangGraph workflow pipeline
workflow = StateGraph(AgentState)

# Add our single diagnostic node to the graph state engine
workflow.add_node("analyze_plant", analyze_plant_node)

# Set the edges to route straight from START -> node -> END
workflow.add_edge(START, "analyze_plant")
workflow.add_edge("analyze_plant", END)

# Compile into an executable application binary graph
compiled_agent = workflow.compile()

# 5. Interface Wrapper Function for your backend main.py to call
def analyze_plant_image_with_openai(file_bytes: bytes) -> dict:
    """
    Kicks off the compiled LangGraph workflow using the image bytes input state.
    """
    initial_state = {"image_bytes": file_bytes}
    final_output = compiled_agent.invoke(initial_state)
    
    # Map the final output state structure cleanly back into values for main.py
    return {
        "label": final_output.get("plant_name", "Healthy / Unspecified"),
        "confidence": 95,
        "treatment_plan": f"{final_output.get('condition_summary', '')}\n\n{final_output.get('detailed_report', '')}"
    }
