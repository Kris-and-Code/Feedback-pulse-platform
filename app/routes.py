from flask import Blueprint, request, jsonify
from app.scraper import scrape_reviews
from app.firebase_service import save_review_to_db
from app.sentiment_analysis import analyze_sentiment
from app.emotion_analysis import analyze_emotion
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import db
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Define the Blueprint
api_routes = Blueprint('api', __name__)

# Root route for API
@api_routes.route('/', methods=['GET'])
def index():
    return "Welcome to the Review Parser API!", 200

# Endpoint to scrape reviews from a URL
@api_routes.route('/scrape-review', methods=['POST'])
def scrape_review():
    # Validate Firebase credentials before proceeding
    if not os.getenv('FIREBASE_PRIVATE_KEY'):
        return jsonify({"error": "Firebase credentials not configured"}), 500
        
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        reviews = scrape_reviews(url)
        response = save_review_to_db(url, reviews)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to aggregate sentiment
@api_routes.route('/aggregate-sentiment', methods=['GET'])
def aggregate_sentiment():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Mock sentiment aggregation logic
    return jsonify({"sentiment": "positive"})

# Endpoint to aggregate emotion
@api_routes.route('/aggregate-emotion', methods=['GET'])
def aggregate_emotion():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    # Mock emotion aggregation logic
    return jsonify({"emotion": "happy"})

class ReviewAnalyzer:
    def __init__(self):
        self.firebase_app = firebase_admin.initialize_app()
        self.db_ref = db.reference('reviews')

    def scrape_review(self):
        url = request.form.get('url')
        
        try:
            # Fetch HTML content
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract reviews (this will need to be customized based on the website structure)
            reviews = self.extract_reviews(soup)
            
            # Save to JSON and database
            with open('reviews.json', 'w') as f:
                json.dump(reviews, f)
            
            self.save_review_to_db(url, reviews)
            
            return jsonify({'status': 'success'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def save_review_to_db(self, url, reviews):
        url_ref = self.db_ref.child(self.clean_url(url))
        
        with ThreadPoolExecutor() as executor:
            for review in reviews:
                review_ref = url_ref.push(review)
                # Start async processing
                executor.submit(self.sentiment_review, review_ref.key)
                executor.submit(self.emotion_review, review_ref.key)

    async def sentiment_review(self, review_id):
        review = self.db_ref.child(review_id).get()
        # Implement sentiment analysis model call here
        sentiment = self.analyze_sentiment(review['text'])
        self.db_ref.child(review_id).update({'sentiment': sentiment})

    async def emotion_review(self, review_id):
        review = self.db_ref.child(review_id).get()
        # Implement emotion analysis model call here
        emotion = self.analyze_emotion(review['text'])
        self.db_ref.child(review_id).update({'emotion': emotion})

    def calculate_aggregate_review_sentiment(self):
        url = request.args.get('url')
        reviews = self.db_ref.child(self.clean_url(url)).get()
        
        sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
        for review in reviews.values():
            sentiments[review['sentiment']] += 1
            
        total = sum(sentiments.values())
        return jsonify({
            sentiment: count/total 
            for sentiment, count in sentiments.items()
        })

    def calculate_aggregate_review_emotion(self):
        url = request.args.get('url')
        reviews = self.db_ref.child(self.clean_url(url)).get()
        
        emotions = {'happy': 0, 'sad': 0, 'angry': 0, 'neutral': 0}
        for review in reviews.values():
            emotions[review['emotion']] += 1
            
        total = sum(emotions.values())
        return jsonify({
            emotion: count/total 
            for emotion, count in emotions.items()
        })
