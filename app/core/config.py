import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Review Analysis API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH")

settings = Settings() 