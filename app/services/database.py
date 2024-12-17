import logging
import sqlite3
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize logger
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(__file__).parent.parent / 'data' / 'feedback.db'
        self._init_db()

    def _init_db(self):
        """Initialize the database and create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        review_text TEXT NOT NULL,
                        rating INTEGER NOT NULL,
                        sentiment_score REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
            self.logger.info("Database connection established successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    def store_feedback(self, review_text, rating, sentiment_score):
        """Store feedback data in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO feedback (review_text, rating, sentiment_score)
                    VALUES (?, ?, ?)
                ''', (review_text, rating, sentiment_score))
                conn.commit()
            self.logger.debug(f"Stored feedback with rating {rating} and sentiment {sentiment_score}")
        except sqlite3.Error as e:
            self.logger.error(f"Error storing feedback: {e}")
            raise

    def get_all_feedback(self):
        """Retrieve all feedback from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM feedback')
                return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving feedback: {e}")
            raise

    def get_feedback_by_rating(self, rating):
        """Retrieve feedback filtered by rating"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM feedback WHERE rating = ?', (rating,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving feedback by rating: {e}")
            raise

class FirebaseService:
    def __init__(self):
        try:
            # Initialize Firebase with your credentials
            cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            logger.warning("Missing Firebase configuration values")
            self.db = None

    async def save_reviews(self, url: str, reviews: list):
        if not self.db:
            logger.warning("Firebase not initialized, returning dummy data")
            return ["dummy_id_1", "dummy_id_2"]
            
        try:
            url_ref = self.db.collection('reviews').document(url)
            url_ref.set({'url': url})
            
            review_ids = []
            for review in reviews:
                review_ref = url_ref.collection('review_items').document()
                review_ref.set(review.dict())
                review_ids.append(review_ref.id)
            
            return review_ids
        except Exception as e:
            logger.error(f"Error saving reviews: {str(e)}")
            raise

    async def get_review(self, id: str):
        if not self.db:
            return {"text": "dummy review", "rating": "5", "date": "2024-03-21"}
            
        try:
            review_doc = self.db.collection('reviews').document(id).get()
            return review_doc.to_dict()
        except Exception as e:
            logger.error(f"Error getting review: {str(e)}")
            raise

    async def update_review(self, id: str, data: dict):
        if not self.db:
            return
            
        try:
            self.db.collection('reviews').document(id).update(data)
        except Exception as e:
            logger.error(f"Error updating review: {str(e)}")
            raise

firebase_service = FirebaseService()
