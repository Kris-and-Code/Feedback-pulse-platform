import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Flask
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

# Firebase
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
FIREBASE_COLLECTION = os.getenv("FIREBASE_COLLECTION", "reviews")
FIREBASE_ANALYZED_COLLECTION = os.getenv("FIREBASE_ANALYZED_COLLECTION", "analyzed_reviews")

# Models
MODEL_PATH_SENTIMENT = os.getenv(
    "MODEL_PATH_SENTIMENT",
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)
MODEL_PATH_EMOTION = os.getenv(
    "MODEL_PATH_EMOTION",
    "j-hartmann/emotion-english-distilroberta-base",
)
MODEL_PATH_VECTORIZER = os.getenv("MODEL_PATH_VECTORIZER", "all-MiniLM-L6-v2")

# Storage
SQLITE_DB_PATH = PROJECT_ROOT / "data" / "feedback.db"
SAMPLE_CSV_PATH = PROJECT_ROOT / "sample_reviews.csv"
AMAZON_SAMPLE_CSV_PATH = PROJECT_ROOT / "data" / "amazon_reviews.csv"
