from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
import shutil
import os

from .database import Base, engine, SessionLocal
from .models import ScanHistory
from .auth import get_db, register_user, login_user
from .scan_engine import calculate_sha256, scan_with_yara
from .ai_engine import predict_malware
from .socket_server import socket_app

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/ws", socket_app)


@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    register_user(username, password, db)
    return {"message": "User registered"}


@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    token = login_user(username, password, db)
    return {"access_token": token}


@app.post("/scan")
async def scan_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_path = f"uploads/{file.filename}"
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    sha256 = calculate_sha256(upload_path)
    yara_result = scan_with_yara(upload_path)

    file_size = os.path.getsize(upload_path)
    ai_prediction, confidence = predict_malware(file_size)

    threat = "HIGH" if yara_result != "Clean" or ai_prediction == "Malicious" else "LOW"

    scan_record = ScanHistory(
        filename=file.filename,
        sha256=sha256,
        yara_result=yara_result,
        ai_prediction=ai_prediction,
        confidence=confidence,
        threat_level=threat
    )

    db.add(scan_record)
    db.commit()

    return {
        "filename": file.filename,
        "sha256": sha256,
        "yara_result": yara_result,
        "ai_prediction": ai_prediction,
        "confidence": confidence,
        "threat_level": threat
    }