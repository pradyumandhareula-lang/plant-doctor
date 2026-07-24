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
    # 1. Grab the fresh image bytes sent from the frontend request
    img_bytes = state.get("image_bytes")
    if not img_bytes:
        return {"plant_name": "Unknown", "condition_summary": "No image uploaded"}

    # 2. Encode the unique bytes payload to base64 string dynamically
    base64_image = base64.b64encode(img_bytes).decode("utf-8")

    # 3. Initialize your ChatOpenAI vision-capable model
    # (Using gpt-4o or gpt-4o-mini for vision processing tasks)
    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=500)

    # 4. Construct a structured multimodal message payload
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Analyze this plant photo. Identify its name exactly, diagnose its health state, and provide a short summary response."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )

    # 5. Invoke the model directly with the fresh contents
    response = model.invoke([message])
    
    # Parse your response.text content out or assign variables here based on model text output
    # (Adjust this part if you are using structured output or Pydantic parsers)
    output_text = response.content

    # 6. Return the updated values back to update the LangGraph state
    return {
        "plant_name": "Extracted Plant Name", # Parse from output_text if needed
        "condition_summary": output_text
    }
