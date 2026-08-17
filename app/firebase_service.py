import os
import uuid
from pathlib import Path

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

load_dotenv()

_db = None
_in_memory_store = {}
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _credentials_path():
    configured = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    default_path = PROJECT_ROOT / "firebase-credentials.json"
    if default_path.exists():
        return default_path

    return None


def is_firebase_configured():
    if _credentials_path() is not None:
        return True
    return bool(os.getenv("FIREBASE_PRIVATE_KEY"))


def _initialize_firebase():
    if firebase_admin._apps:
        return

    credentials_path = _credentials_path()
    if credentials_path is not None:
        cred = credentials.Certificate(str(credentials_path))
        firebase_admin.initialize_app(cred)
        return

    firebase_config = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
    }
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)


def _get_db():
    global _db
    if _db is not None:
        return _db

    if not is_firebase_configured():
        raise RuntimeError("Firebase credentials not configured")

    _initialize_firebase()
    _db = firestore.client()
    return _db


def _reviews_collection_name():
    return os.getenv("FIREBASE_COLLECTION", "reviews")


def save_review_to_db(url, reviews):
    if not is_firebase_configured():
        stored = _in_memory_store.setdefault(url, [])
        for review in reviews:
            stored.append({**review, "id": str(uuid.uuid4())})
        return {
            "message": "Reviews saved to in-memory store (Firebase not configured)",
            "count": len(reviews),
            "storage": "memory",
        }

    db = _get_db()
    collection = _reviews_collection_name()
    url_doc = db.collection(collection).document(url)
    url_doc.set({"url": url}, merge=True)

    for review in reviews:
        review_ref = url_doc.collection("reviews").document()
        review_ref.set(review)

    return {
        "message": "Reviews saved successfully",
        "count": len(reviews),
        "storage": "firebase",
        "collection": collection,
    }


def get_reviews_for_url(url):
    if not is_firebase_configured():
        return _in_memory_store.get(url, [])

    db = _get_db()
    collection = _reviews_collection_name()
    url_doc = db.collection(collection).document(url)
    review_docs = url_doc.collection("reviews").stream()
    return [doc.to_dict() for doc in review_docs]
