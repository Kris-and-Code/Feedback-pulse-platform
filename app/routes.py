import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

from app.data_loader import load_reviews_from_csv
from app.emotion_analysis import aggregate_emotions, analyze_emotion
from app.firebase_service import get_reviews_for_url, is_firebase_configured, save_review_to_db
from app.scraper import scrape_reviews
from app.sentiment_analysis import aggregate_sentiments, analyze_sentiment

load_dotenv()

api_routes = Blueprint("api", __name__)


@api_routes.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "message": "Welcome to the Feedback Pulse API",
            "firebase_configured": is_firebase_configured(),
            "endpoints": {
                "health": "GET /health",
                "scrape_review": "POST /scrape-review",
                "analyze_text": "POST /analyze-text",
                "analyze_csv": "POST /analyze-csv",
                "aggregate_sentiment": "GET /aggregate-sentiment?url=<url>",
                "aggregate_emotion": "GET /aggregate-emotion?url=<url>",
            },
        }
    )


@api_routes.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "firebase_configured": is_firebase_configured()}), 200


@api_routes.route("/scrape-review", methods=["POST"])
def scrape_review():
    data = request.get_json()
    url = data.get("url") if data else None
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        reviews = scrape_reviews(url)
        if isinstance(reviews, dict) and "error" in reviews:
            return jsonify(reviews), 502

        response = save_review_to_db(url, reviews)
        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@api_routes.route("/analyze-text", methods=["POST"])
def analyze_text():
    data = request.get_json() or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "text is required"}), 400

    return jsonify(
        {
            "text": text,
            "sentiment": analyze_sentiment(text),
            "emotion": analyze_emotion(text),
        }
    )


@api_routes.route("/analyze-csv", methods=["POST"])
def analyze_csv():
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required (field name: file)"}), 400

    upload = request.files["file"]
    if not upload.filename or not upload.filename.lower().endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    try:
        reviews = load_reviews_from_csv(file_content=upload.read())
        results = []
        for review in reviews:
            text = f"{review.get('review_title', '')} {review['text']}".strip()
            results.append(
                {
                    **review,
                    "sentiment": analyze_sentiment(text),
                    "emotion": analyze_emotion(text),
                }
            )

        return jsonify(
            {
                "total_reviews": len(results),
                "results": results,
                "summary": {
                    "sentiment_distribution": aggregate_sentiments(reviews),
                    "emotion_distribution": aggregate_emotions(reviews),
                },
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@api_routes.route("/aggregate-sentiment", methods=["GET"])
def aggregate_sentiment():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    reviews = get_reviews_for_url(url)
    if not reviews:
        return jsonify({"error": "No reviews found for this URL"}), 404

    return jsonify({"url": url, "sentiment_distribution": aggregate_sentiments(reviews)})


@api_routes.route("/aggregate-emotion", methods=["GET"])
def aggregate_emotion():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    reviews = get_reviews_for_url(url)
    if not reviews:
        return jsonify({"error": "No reviews found for this URL"}), 404

    return jsonify({"url": url, "emotion_distribution": aggregate_emotions(reviews)})
