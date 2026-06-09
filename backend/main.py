from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from agent import plant_ai_agent

# 1. Initialize the application
app = FastAPI(title="Plant Doctor API")
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Welcome to the Plant Doctor API Server!"}

# 2. This endpoint receives the plant image, runs the AI, and saves to database
@app.post("/diagnose")
async def diagnose_plant_upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # Read the uploaded file bytes
        image_bytes = await file.read()
        
        # Run our LangGraph AI agent brain
        ai_input = {"image_bytes": image_bytes}
        ai_output = plant_ai_agent.invoke(ai_input)
        
        # Create a database record with the results
        new_diagnostic = models.PlantDiagnostic(
            plant_name=ai_output.get("plant_name", "Unknown"),
            condition_summary=ai_output.get("condition_summary", "Unknown Issue"),
            detailed_report=ai_output.get("detailed_report", "No report details generated."),
            image_path=file.filename
        )
        
        # Save to SQLite database
        db.add(new_diagnostic)
        db.commit()
        db.refresh(new_diagnostic)
        
        return new_diagnostic
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/diagnostics")
def get_diagnostics(db: Session = Depends(get_db)):
    return db.query(models.PlantDiagnostic).all()