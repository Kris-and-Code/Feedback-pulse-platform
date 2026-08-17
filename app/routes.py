import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

from app.amazon_scraper import scrape_amazon_reviews
from app.batch_analyzer import analyze_reviews_batch, get_summary_stats
from app.data_loader import load_reviews_from_csv
from app.emotion_analysis import (
    aggregate_emotions,
    analyze_emotion,
    analyze_emotion_detailed,
    analyze_emotion_ml,
)
from app.firebase_service import (
    get_analyzed_reviews,
    get_reviews_for_url,
    is_firebase_configured,
    push_analyzed_results,
    save_review_to_db,
)
from app.local_db import get_all_feedback, get_feedback_by_rating, store_feedback
from app.scraper import scrape_reviews
from app.sentiment_analysis import aggregate_sentiments, analyze_sentiment, analyze_sentiment_detailed
from app.vectorizer import encode_text, find_similar_reviews

load_dotenv()

api_routes = Blueprint("api", __name__)


def _analyze_by_mode(text, mode):
    if mode == "detailed":
        return {
            "sentiment": analyze_sentiment_detailed(text),
            "emotion": analyze_emotion_detailed(text),
        }
    if mode == "ml":
        return {
            "sentiment": analyze_sentiment_detailed(text),
            "emotion": analyze_emotion_ml(text),
        }
    return {
        "sentiment": analyze_sentiment(text),
        "emotion": analyze_emotion(text),
    }


@api_routes.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "message": "Welcome to the Feedback Pulse API",
            "firebase_configured": is_firebase_configured(),
            "endpoints": {
                "health": "GET /health",
                "scrape_review": "POST /scrape-review",
                "scrape_amazon": "POST /scrape-amazon",
                "analyze_text": "POST /analyze-text",
                "analyze_csv": "POST /analyze-csv",
                "find_similar": "POST /find-similar",
                "vectorize": "POST /vectorize",
                "feedback_list": "GET /feedback",
                "feedback_create": "POST /feedback",
                "analyzed_reviews": "GET /analyzed-reviews",
                "aggregate_sentiment": "GET /aggregate-sentiment?url=<url>",
                "aggregate_emotion": "GET /aggregate-emotion?url=<url>",
            },
            "legacy_endpoints": {
                "status": "GET /api/status",
                "analyze_sentiment": "POST /api/analyze-sentiment",
                "analyze_emotion": "POST /api/analyze-emotion",
                "parse_text": "POST /api/parse-text",
                "parse_file": "POST /api/parse-file",
                "find_similar": "POST /api/find-similar",
                "scrape_reviews": "POST /api/scrape-reviews",
            },
            "analyze_modes": ["simple", "detailed", "ml"],
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


@api_routes.route("/scrape-amazon", methods=["POST"])
def scrape_amazon():
    data = request.get_json() or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "Amazon product URL is required"}), 400

    try:
        reviews = scrape_amazon_reviews(url)
        if isinstance(reviews, dict) and "error" in reviews:
            return jsonify(reviews), 502

        response = save_review_to_db(url, reviews)
        return jsonify({**response, "source": "amazon"})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@api_routes.route("/analyze-text", methods=["POST"])
def analyze_text():
    data = request.get_json() or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "text is required"}), 400

    mode = data.get("mode", "simple")
    if mode not in ("simple", "detailed", "ml"):
        return jsonify({"error": "mode must be one of: simple, detailed, ml"}), 400

    result = _analyze_by_mode(text, mode)
    return jsonify({"text": text, "mode": mode, **result})


@api_routes.route("/analyze-csv", methods=["POST"])
def analyze_csv():
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required (field name: file)"}), 400

    upload = request.files["file"]
    if not upload.filename or not upload.filename.lower().endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    mode = request.form.get("mode", "simple")
    if mode not in ("simple", "detailed", "ml"):
        return jsonify({"error": "mode must be one of: simple, detailed, ml"}), 400

    include_vector = request.form.get("include_vector", "false").lower() == "true"
    push_to_firebase = request.form.get("push_to_firebase", "false").lower() == "true"

    try:
        reviews = load_reviews_from_csv(file_content=upload.read())
        results = analyze_reviews_batch(reviews, mode=mode, include_vector=include_vector)
        summary = get_summary_stats(results)

        response = {
            "total_reviews": len(results),
            "mode": mode,
            "results": results,
            "summary": summary,
        }

        if push_to_firebase:
            response["firebase"] = push_analyzed_results(results)

        return jsonify(response)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@api_routes.route("/find-similar", methods=["POST"])
def find_similar():
    data = request.get_json() or {}
    query_text = data.get("text")
    if not query_text:
        return jsonify({"error": "text is required"}), 400

    top_k = int(data.get("top_k", 5))
    reviews = data.get("reviews")
    url = data.get("url")

    if reviews is None and url:
        reviews = get_reviews_for_url(url)

    if not reviews:
        file_path = data.get("csv_path", "sample_reviews.csv")
        if os.path.exists(file_path):
            reviews = load_reviews_from_csv(file_path=file_path)

    if not reviews:
        return jsonify({"error": "No reviews available for similarity search"}), 400

    similar = find_similar_reviews(query_text, reviews, top_k=top_k)
    return jsonify({"query": query_text, "top_k": top_k, "similar_reviews": similar})


@api_routes.route("/vectorize", methods=["POST"])
def vectorize():
    data = request.get_json() or {}
    text = data.get("text")
    if not text:
        return jsonify({"error": "text is required"}), 400

    embedding = encode_text(text)
    return jsonify({"text": text, "embedding_dimension": len(embedding), "embedding": embedding})


@api_routes.route("/feedback", methods=["GET"])
def list_feedback():
    rating = request.args.get("rating")
    if rating is not None:
        try:
            feedback = get_feedback_by_rating(float(rating))
        except ValueError:
            return jsonify({"error": "rating must be a number"}), 400
    else:
        feedback = get_all_feedback()

    return jsonify({"count": len(feedback), "feedback": feedback})


@api_routes.route("/feedback", methods=["POST"])
def create_feedback():
    data = request.get_json() or {}
    review_text = data.get("review_text") or data.get("text")
    rating = data.get("rating")

    if not review_text:
        return jsonify({"error": "review_text is required"}), 400
    if rating is None:
        return jsonify({"error": "rating is required"}), 400

    try:
        rating_value = float(rating)
    except (TypeError, ValueError):
        return jsonify({"error": "rating must be a number"}), 400

    mode = data.get("mode", "simple")
    analysis = _analyze_by_mode(review_text, mode if mode in ("simple", "detailed", "ml") else "simple")
    sentiment = analysis["sentiment"]
    emotion = analysis["emotion"]
    if isinstance(sentiment, dict):
        sentiment = sentiment.get("sentiment")
    if isinstance(emotion, dict):
        emotion = emotion.get("primary_emotion", emotion)

    feedback_id = store_feedback(review_text, rating_value, str(sentiment), str(emotion))
    return jsonify(
        {
            "id": feedback_id,
            "review_text": review_text,
            "rating": rating_value,
            "sentiment": sentiment,
            "emotion": emotion,
            "storage": "sqlite",
        }
    ), 201


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


@api_routes.route("/analyzed-reviews", methods=["GET"])
def analyzed_reviews():
    return jsonify({"count": len(get_analyzed_reviews()), "results": get_analyzed_reviews()})
