from flask import Blueprint, request, jsonify
from app.scraper import scrape_reviews
from app.firebase_service import save_review_to_db
from app.sentiment_analysis import analyze_sentiment
from app.emotion_analysis import analyze_emotion
import os
from dotenv import load_dotenv

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
