import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Firebase configuration
FIREBASE_CONFIG = {
    'project_id': os.getenv('FIREBASE_PROJECT_ID'),
    'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    'private_key': os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
    'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
    'client_id': os.getenv('FIREBASE_CLIENT_ID'),
    'auth_uri': os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
    'token_uri': os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
    'auth_provider_x509_cert_url': os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_CERT_URL'),
    'type': 'service_account'
}

# Scraping configuration
SCRAPER_CONFIG = {
    'USER_AGENT': os.getenv('USER_AGENT'),
    'TIMEOUT': int(os.getenv('REQUEST_TIMEOUT', 30)),
    'MAX_RETRIES': int(os.getenv('MAX_RETRIES', 3))
}

# Analysis configuration
ANALYZER_CONFIG = {
    'MAX_TEXT_LENGTH': int(os.getenv('MAX_TEXT_LENGTH', 512)),
    'MIN_CONFIDENCE_SCORE': float(os.getenv('MIN_CONFIDENCE_SCORE', 0.6)),
    'MODEL_NAME': os.getenv('MODEL_NAME', 'distilbert-base-uncased-finetuned-sst-2-english')
}

# Application configuration
APP_CONFIG = {
    'ENV': os.getenv('FLASK_ENV', 'development'),
    'DEBUG': bool(int(os.getenv('FLASK_DEBUG', 1))),
    'PORT': int(os.getenv('PORT', 5000)),
    'HOST': os.getenv('HOST', '0.0.0.0')
}

# Security configuration
SECURITY_CONFIG = {
    'SECRET_KEY': os.getenv('SECRET_KEY', 'your-secret-key-here'),
    'ALLOWED_ORIGINS': os.getenv('ALLOWED_ORIGINS', '').split(',')
}

class Config:
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    MODEL_PATH_SENTIMENT = os.getenv('MODEL_PATH_SENTIMENT', 'distilbert-base-uncased-finetuned-sst-2-english')
    MODEL_PATH_EMOTION = os.getenv('MODEL_PATH_EMOTION', 'j-hartmann/emotion-english-distilroberta-base')

    @classmethod
    def validate_config(cls):
        if not cls.FIREBASE_CREDENTIALS_PATH:
            logger.warning("FIREBASE_CREDENTIALS_PATH not set. Running in development mode.")
        elif not os.path.exists(cls.FIREBASE_CREDENTIALS_PATH):
            logger.warning(f"Firebase credentials file not found at: {cls.FIREBASE_CREDENTIALS_PATH}")

# Validate configuration on import
Config.validate_config()
