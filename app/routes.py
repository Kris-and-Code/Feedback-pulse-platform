import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

from app.emotion_analysis import analyze_emotion
from app.firebase_service import save_review_to_db
from app.scraper import scrape_reviews
from app.sentiment_analysis import analyze_sentiment

load_dotenv()

api_routes = Blueprint("api", __name__)


@api_routes.route("/", methods=["GET"])
def index():
    return "Welcome to the Review Parser API!", 200


@api_routes.route("/scrape-review", methods=["POST"])
def scrape_review():
    if not os.getenv("FIREBASE_PRIVATE_KEY"):
        return jsonify({"error": "Firebase credentials not configured"}), 500

    data = request.get_json()
    url = data.get("url") if data else None
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        reviews = scrape_reviews(url)
        response = save_review_to_db(url, reviews)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_routes.route("/aggregate-sentiment", methods=["GET"])
def aggregate_sentiment():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    return jsonify({"sentiment": "positive"})


@api_routes.route("/aggregate-emotion", methods=["GET"])
def aggregate_emotion():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    return jsonify({"emotion": "happy"})
