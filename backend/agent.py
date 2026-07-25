import os
import base64
import json
import hashlib
from openai import OpenAI

# Automatically captures your credentials from environment configs
client = OpenAI()

def analyze_plant_image_with_openai(*args, **kwargs):
    """
    Processes raw visual payloads, generates a unique signature tracking code,
    and requests live diagnostic completions from the specified neural model matrix.
    """
    # Dynamically extract image bytes whether passed as 'img_bytes' or 'file_bytes'
    img_bytes = kwargs.get('img_bytes') or kwargs.get('file_bytes')
    if not img_bytes and args:
        img_bytes = args[0]
        
    model_name = kwargs.get('model_name', 'gpt-4o')

    # 1. Generate unique deterministic ID directly from image data to resolve history logs
    sha256_hash = hashlib.sha256(img_bytes).hexdigest()
    target_system_id = f"PLNT-HEX-{sha256_hash[:12].upper()}"

    # 2. Convert raw image binaries into base64 visual vectors
    base64_image = base64.b64encode(img_bytes).decode('utf-8')
    
    # 3. Establish clear prompt guardrails requesting a dictionary output
    system_prompt = (
        "You are an expert plant pathologist AI system. Diagnose the plant provided in the image. "
        "You must return your analysis strictly as a valid JSON object containing exactly two keys:\n"
        "1. 'confidence': A string representing your specific identification certainty (e.g., '94%').\n"
        "2. 'treatment_plan': A detailed markdown document outlining identified symptoms and immediate curative actions."
    )

    try:
        # 4. Dispatch live vision token payloads dynamically using your exact frontend adjustments
        response = client.chat.completions.create(
            model=model_name, # 👈 Linked to frontend selection
            response_format={"type": "json_object"}, # Guarantees parseable outputs
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Execute rigorous pathogenetic classification diagnostics on this image matrix."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            temperature=temperature # 👈 Linked to frontend slider choice
        )

        # 5. Extract structured json results using modern object dot-notation parameters
        raw_json_output = response.choices[0].message.content
        parsed_result = json.loads(raw_json_output)

        return {
            "target_system_id": target_system_id,
            "core_target_confidence": parsed_result.get("confidence", "Unknown %"),
            "treatment_plan": parsed_result.get("treatment_plan", "No structural mitigation strategy parsed.")
        }

    except Exception as api_execution_fault:
        # Secure boundary failover fallback matrix tracking container
        return {
            "target_system_id": target_system_id,
            "core_target_confidence": "0% (Pipeline Failure)",
            "treatment_plan": f"### ⚠️ Vision Recognition Pipeline Failure\nAn anomaly occurred inside the backend engine pipeline: `{str(api_execution_fault)}`"
        }
