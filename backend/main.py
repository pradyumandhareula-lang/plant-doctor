from fastapi import FastAPI, UploadFile, File
import sqlite3
import base64
import json
from openai import OpenAI
import os

app = FastAPI()

# Initialize Database
DB_FILE = "history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            species TEXT,
            issue TEXT,
            plan TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.post("/diagnose")
async def diagnose_plant(file: UploadFile = File(...)):
    # --- Keep your existing OpenAI API configuration here ---
    # (Assuming client = OpenAI(api_key=...) handles the call)
    
    # Example placeholder variables of what your OpenAI parsing extracts:
    species = "Snake Plant (Sansevieria)"
    issue = "Low Light Etiolation (95%)"
    plan = "Relocate closer to a south window. Prune weakened leaves. Water every 3-4 weeks."
    
    # Save to SQLite Database automatically
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scans (species, issue, plan) VALUES (?, ?, ?)",
        (species, issue, plan)
    )
    conn.commit()
    conn.close()
    
    return {"diagnosis": f"### Identified: {species}\n\n⚠️ {issue}\n\n📋 {plan}"}

@app.get("/history")
async def get_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, species, issue, plan FROM scans ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    
    history_list = []
    for row in rows:
        history_list.append({
            "timestamp": row[0],
            "species": row[1],
            "issue": row[2],
            "plan": row[3]
        })
    return {"history": history_list}
