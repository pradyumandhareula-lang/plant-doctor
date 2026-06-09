import os
import base64
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

class AgentState(TypedDict):
    image_bytes: bytes
    plant_name: str
    condition_summary: str
    detailed_report: str

def analyze_plant_node(state: AgentState) -> dict:
    # Check if OpenAI Key exists in the environment settings
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            model = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=api_key)
            base64_image = base64.b64encode(state["image_bytes"]).decode("utf-8")
            
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "Analyze this plant. Return EXACTLY 3 lines separated by '|' like this: Plant Name | Condition Summary | Detailed Step-by-Step Care Instructions."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            )
            response = model.invoke([message])
            parts = response.content.split("|")
            return {
                "plant_name": parts[0].strip(),
                "condition_summary": parts[1].strip(),
                "detailed_report": parts[2].strip()
            }
        except Exception:
            pass # If API fails or breaks, drop down to the simulation fallback below
            
    # Mock Simulation Fallback (Option C placeholder)
    return {
        "plant_name": "Monstera Deliciosa (Swiss Cheese Plant)",
        "condition_summary": "Leaf Leaf-Spot Disease / Fungal Infection",
        "detailed_report": (
            "1. Diagnosis: Small brown spots with yellow halos indicating a fungal leaf-spot issue.\n"
            "2. Immediate Action: Prune away highly infected leaves immediately using clean shears.\n"
            "3. Watering Care: Reduce watering frequency. Only water when the top 2 inches of soil are dry.\n"
            "4. Treatment: Spray the remaining foliage with organic Neem Oil once every 7 days."
        )
    }

workflow = StateGraph(AgentState)
workflow.add_node("analyzer", analyze_plant_node)
workflow.add_edge(START, "analyzer")
workflow.add_edge("analyzer", END)
plant_ai_agent = workflow.compile()