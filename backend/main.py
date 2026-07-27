import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from passlib.context import CryptContext
from PIL import Image
import io

# Import your agent functions from agent.py
from agent import analyze_plant_image, compare_weekly_photos

app = FastAPI()

# Password Hashing Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------
# 1. Database Initialization
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    # Plants Registry Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plant_name TEXT NOT NULL,
            species TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Diagnosis History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id INTEGER NOT NULL,
            diagnosis_result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(plant_id) REFERENCES plants(id)
        )
    """)
    conn.commit()
    conn.close()


# Run database setup on startup
init_db()


def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------
# 2. Pydantic Models for Request Validation
# ---------------------------------------------------------
class UserAuth(BaseModel):
    username: str
    password: str


class PlantCreate(BaseModel):
    user_id: int
    plant_name: str
    species: str


# ---------------------------------------------------------
# 3. Authentication Endpoints (/register, /login)
# ---------------------------------------------------------
@app.post("/register")
def register(user: UserAuth):
    hashed_password = pwd_context.hash(user.password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (user.username, hashed_password),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()
    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: UserAuth):
    conn = get_db()
    cursor = conn.cursor()
    db_user = cursor
    .execute("SELECT * FROM users WHERE username = ?", (user.username,))
    .fetchone()
    conn.close()

    if not db_user or not pwd_context.verify(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user["id"],
        "username": db_user["username"],
    }


# ---------------------------------------------------------
# 4. Plant Registry Endpoints (/plants)
# ---------------------------------------------------------
@app.post("/plants")
def add_plant(plant: PlantCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO plants (user_id, plant_name, species) VALUES (?, ?, ?)",
        (plant.user_id, plant.plant_name, plant.species),
    )
    conn.commit()
    plant_id = cursor.lastrowid
    conn.close()
    return {"message": "Plant added successfully", "plant_id": plant_id}


@app.get("/plants/{user_id}")
def get_user_plants(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    plants = cursor.execute(
        "SELECT * FROM plants WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {"plants": [dict(p) for p in plants]}


# ---------------------------------------------------------
# 5. Vision AI Endpoints (Diagnosis & Weekly Check-In)
# ---------------------------------------------------------
@app.post("/api/diagnose")
async def diagnose(plant_id: int = Form(...), file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Call AI model from agent.py
        diagnosis_result = analyze_plant_image(image)

        # Save result to SQLite
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO diagnosis_history (plant_id, diagnosis_result) VALUES (?, ?)",
            (plant_id, str(diagnosis_result)),
        )
        conn.commit()
        conn.close()

        return {"success": True, "data": diagnosis_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/compare")
async def compare_photos(
    previous_photo: UploadFile = File(...), current_photo: UploadFile = File(...)
):
    try:
        prev_img = Image.open(io.BytesIO(await previous_photo.read()))
        curr_img = Image.open(io.BytesIO(await current_photo.read()))

        # Call dual-image comparison from agent.py
        comparison_result = compare_weekly_photos(prev_img, curr_img)
        return {"success": True, "data": comparison_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
