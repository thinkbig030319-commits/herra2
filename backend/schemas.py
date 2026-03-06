from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class ScanResponse(BaseModel):
    filename: str
    sha256: str
    yara_result: str
    ai_prediction: str
    confidence: float
    threat_level: str