import os
import sqlite3
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Plant Doctor AI API")

DB_PATH = "database.db"

# --- DATABASE SETUP ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Plants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plant_name TEXT NOT NULL,
            species TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Diagnoses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER NOT NULL,
            diagnosis_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plant_id) REFERENCES plants (id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# --- PYDANTIC SCHEMAS ---
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PlantCreate(BaseModel):
    user_id: int
    plant_name: str
    species: Optional[str] = None

# --- AUTH ROUTES ---
@app.post("/register")
def register(user: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
        conn.commit()
        return {"message": "User created successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE username = ? AND password = ?", (user.username, user.password))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"user_id": row["id"], "username": row["username"]}

# --- PLANT REGISTRY ROUTES ---
@app.post("/plants")
def add_plant(plant: PlantCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO plants (user_id, plant_name, species) VALUES (?, ?, ?)",
                   (plant.user_id, plant.plant_name, plant.species))
    conn.commit()
    plant_id = cursor.lastrowid
    conn.close()
    return {"message": "Plant added", "plant_id": plant_id}

@app.get("/plants/{user_id}")
def get_plants(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, plant_name, species, created_at FROM plants WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    plants = [dict(row) for row in rows]
    return {"plants": plants}

# --- DIAGNOSIS ROUTE ---
@app.post("/api/diagnose")
async def diagnose_endpoint(plant_id: int = Form(...), file: UploadFile = File(...)):
    try:
        from backend.agent import analyze_plant_image
        contents = await file.read()
        result = analyze_plant_image(image_bytes=contents)
        
        # Save diagnosis
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO diagnoses (plant_id, diagnosis_text) VALUES (?, ?)", 
                       (plant_id, json.dumps(result)))
        conn.commit()
        conn.close()
        
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- COMPARISON ROUTE ---
@app.post("/api/compare")
async def compare_endpoint(previous_photo: UploadFile = File(...), current_photo: UploadFile = File(...)):
    try:
        from backend.agent import compare_weekly_photos
        prev_bytes = await previous_photo.read()
        curr_bytes = await current_photo.read()
        report = compare_weekly_photos(prev_bytes, curr_bytes)
        return {"status": "success", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
