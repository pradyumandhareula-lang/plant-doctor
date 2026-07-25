import os
import base64
import json
import hashlib
from openai import OpenAI

def analyze_plant_image_with_openai(file_bytes):
    """
    Executes real live AI vision analytics on incoming raw leaf byte streams 
    using OpenAI's official model execution endpoints.
    """
    # 1. Initialize client using environment variable API key
    # Make sure you have your OPENAI_API_KEY set up in your Streamlit secrets/env
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        # 2. Convert raw image bytes to base64 encoding string for OpenAI Vision API
        base64_image = base64.b64encode(file_bytes).decode('utf-8')
        
        # 3. Request absolute live structural JSON inference path from OpenAI core
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": (
                                "Analyze this botanical plant or leaf image carefully. "
                                "Identify the exact plant species, its health issue, and create a curation plan. "
                                "Return a valid JSON object matching this exact key structure:\n"
                                "{\n"
                                '  "target_system_id": "Scientific Genus Species (Common Name) - Pathology State Name",\n'
                                '  "core_target_confidence": "92%",\n'
                                '  "treatment_plan": "### 🩺 Live Botanical Analysis Report\\n**Observed Symptoms:** Description here...\\n\\n### 📋 Curative Playbook Protocol\\n1. **Step One:** Action...\\n2. **Step Two:** Action..."\n'
                                "}"
                            )
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
            temperature=0.2
        )
        
        # 4. Parse output string back into a structural python dictionary matrix
        result_json_string = response.choices[0].message.content
        return json.loads(result_json_string)

    except Exception as api_execution_fault:
        # Fallback error mapping container if network drops or keys expire
        return {
            "target_system_id": "System Analysis Interface Operational Fault",
            "core_target_confidence": "0%",
            "treatment_plan": f"### ❌ Neural Network Connection Interrupted\nAn error occurred while connecting to OpenAI core: {str(api_execution_fault)}"
        }
