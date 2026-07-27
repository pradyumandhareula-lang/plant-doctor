import sqlite3
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import the actual dynamic agent vision function from agent.py
from backend.agent import analyze_plant_image

app = FastAPI(title="Plant Doctor Backend API")

# Enable CORS for Streamlit / Frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "plant_registry.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            species TEXT,
            confidence TEXT,
            treatment_plan TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.get("/")
def read_root():
    return {"status": "Plant Doctor API active and running"}


@app.post("/diagnose")
async def diagnose_plant(file: UploadFile = File(...)):
    """
    Receives an uploaded image file, invokes the AI vision model in agent.py,
    persists the diagnosis to SQLite, and returns the result.
    """
    try:
        # 1. Read raw image bytes from upload
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # 2. Dynamically call the Vision AI Agent model (No fixed literals / placeholders)
        result = analyze_plant_image(image_bytes)

        # 3. Write dynamic results to SQLite registry
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO diagnoses (species, confidence, treatment_plan) VALUES (?, ?, ?)",
            (
                result.get("target_system_id", "Unknown"),
                result.get("core_target_confidence", "N/A"),
                result.get("treatment_plan", "No plan generated.")
            )
        )
        conn.commit()
        conn.close()

        # 4. Return dynamic model diagnosis payload
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Backend Pipeline Error during /diagnose: {str(e)}"
        )
