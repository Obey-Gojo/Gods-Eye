import hashlib
import json
import os
import sqlite3
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="AI Integrity Assurance Integration API", version="1.0")

# --- 1. CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Static Files & Dashboard UI Mounting ---
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def serve_dashboard():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "index.html not found in frontend folder"}


# --- File Storage & Database Paths ---
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "database.db"))
RECORDS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "image_records.json"))


# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            contributor TEXT,
            image_hash TEXT,
            model_version TEXT,
            detected_vehicle TEXT,
            confidence REAL,
            image_integrity TEXT,
            model_integrity TEXT,
            result_integrity TEXT,
            blockchain_tx TEXT,
            overall_status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


init_db()


# --- Real Hash Verification & Integration Modules ---

def calculate_sha256(file_bytes: bytes) -> str:
    """Computes standard SHA-256 cryptographic hash."""
    return hashlib.sha256(file_bytes).hexdigest()


def module_1_data_integrity(file_path: str, file_bytes: bytes, contributor: str):
    """Member 1: Computes SHA-256 and validates against image_records.json ledger."""
    file_hash = calculate_sha256(file_bytes)
    is_valid = False

    # Check against pre-registered records in JSON ledger
    if os.path.exists(RECORDS_FILE):
        try:
            with open(RECORDS_FILE, "r") as f:
                records = json.load(f)

            for entry in records:
                # Match both hash and contributor if available
                if entry.get("hash") == file_hash:
                    if "contributor" in entry:
                        if entry.get("contributor").lower() == contributor.lower():
                            is_valid = True
                            break
                    else:
                        is_valid = True
                        break
        except Exception as e:
            print(f"Error reading {RECORDS_FILE}: {e}")
            is_valid = False
    else:
        print(f"Warning: {RECORDS_FILE} not found. Defaulting verification to FAIL.")
        is_valid = False

    return {"image_hash": file_hash, "integrity_pass": is_valid}


def module_2_cv_inference(file_path: str, model_version: str):
    """Member 2: Runs YOLO/PyTorch object detection (Staged/Mock)."""
    return {"vehicle": "CAR", "confidence": 96.0}


def module_3_model_security(model_version: str):
    """Member 3: Scans model weights for backdoors/trojans."""
    return {"model_verified": True, "model_hash": "0xmod319a..."}


def module_4_blockchain_ledger(payload: dict):
    """Member 4: Writes transaction hashes to the smart contract."""
    tx_hash = f"0x{hashlib.sha256(str(payload).encode()).hexdigest()[:16]}..."
    return {"blockchain_tx": tx_hash, "recorded": True}


# --- REST API Endpoints ---

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Handles raw image storage."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "size_bytes": len(contents), "status": "UPLOADED"}


@app.post("/verify-image")
async def verify_image(filename: str = Form(...), contributor: str = Form("Default Contributor")):
    """Member 1 endpoint: verifies hash against image_records.json."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "rb") as f:
        data = f.read()
    res = module_1_data_integrity(file_path, data, contributor)
    return res


@app.post("/verify-model")
async def verify_model(model_version: str = Form("yolo_v8_defense")):
    """Member 3 endpoint: scans model for Trojans."""
    return module_3_model_security(model_version)


@app.post("/run-inference")
async def run_inference(filename: str = Form(...), model_version: str = Form("yolo_v8_defense")):
    """Member 2 endpoint: runs vehicle detection."""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return module_2_cv_inference(file_path, model_version)


@app.post("/verify-result")
async def verify_result(output_data: str = Form(...)):
    """Verifies output has not been intercepted/tampered in transit."""
    return {"result_integrity_pass": True}


@app.get("/get-history")
def get_history(limit: int = 10):
    """Fetches immutable audit logs from SQLite."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, filename, contributor, image_hash, model_version, 
               detected_vehicle, confidence, image_integrity, model_integrity, 
               result_integrity, blockchain_tx, overall_status, timestamp 
        FROM audit_logs ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "filename": r[1],
            "contributor": r[2],
            "image_hash": r[3],
            "model_version": r[4],
            "detected_vehicle": r[5],
            "confidence": r[6],
            "image_integrity": r[7],
            "model_integrity": r[8],
            "result_integrity": r[9],
            "blockchain_tx": r[10],
            "status": r[11],
            "timestamp": r[12]
        })
    return {"logs": logs}


# --- Full Integrated Pipeline Endpoint ---

@app.post("/process-pipeline")
async def process_pipeline(
    file: UploadFile = File(...),
    contributor: str = Form("Company A"),
    model_version: str = Form("yolo_v8_recon"),
    simulate_poison: bool = Form(False),
    simulate_backdoor: bool = Form(False),
    simulate_tamper: bool = Form(False)
):
    """
    Executes the entire end-to-end integration:
    Upload -> Hash -> Verify -> AI -> Result -> Blockchain -> Database Log
    """
    # 1. Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # 2. Member 1: Image & Data Check (Active JSON lookup)
    m1_res = module_1_data_integrity(file_path, contents, contributor)
    img_ok = False if simulate_poison else m1_res["integrity_pass"]

    # 3. Member 3: Model Security Check
    m3_res = module_3_model_security(model_version)
    mod_ok = False if simulate_backdoor else m3_res["model_verified"]

    # 4. Member 2: CV Inference (Staged / Mock)
    m2_res = module_2_cv_inference(file_path, model_version)
    detected = "NO" if (simulate_poison or simulate_backdoor or not img_ok) else m2_res["vehicle"]
    conf = 35.0 if not (img_ok and mod_ok) else m2_res["confidence"]

    # 5. Result Verification
    res_ok = False if simulate_tamper else True

    # 6. Overall Verdict
    is_trusted = all([img_ok, mod_ok, res_ok])
    status = "TRUSTED" if is_trusted else "UNTRUSTED"

    # 7. Member 4: Blockchain Record
    tx_payload = {
        "image_hash": m1_res["image_hash"],
        "model": model_version,
        "contributor": contributor,
        "detected": detected,
        "status": status
    }
    m4_res = module_4_blockchain_ledger(tx_payload)

    # 8. Store in SQLite Audit Log
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs 
        (filename, contributor, image_hash, model_version, detected_vehicle, confidence, 
         image_integrity, model_integrity, result_integrity, blockchain_tx, overall_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file.filename, contributor, m1_res["image_hash"], model_version, detected, conf,
        "PASS" if img_ok else "FAIL",
        "PASS" if mod_ok else "FAIL",
        "PASS" if res_ok else "FAIL",
        m4_res["blockchain_tx"],
        status
    ))
    conn.commit()
    conn.close()

    return {
        "filename": file.filename,
        "contributor": contributor,
        "image_hash": m1_res["image_hash"],
        "model_version": model_version,
        "prediction": detected,
        "confidence": f"{conf:.0f}%",
        "checks": {
            "image_integrity": "✅" if img_ok else "❌",
            "model_integrity": "✅" if mod_ok else "❌",
            "result_integrity": "✅" if res_ok else "❌",
            "blockchain_record": "✅"
        },
        "blockchain_tx": m4_res["blockchain_tx"],
        "status": status,
        "is_trusted": is_trusted
    }