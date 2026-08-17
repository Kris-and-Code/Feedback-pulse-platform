from flask import Blueprint, jsonify, request

from app.batch_analyzer import analyze_reviews_batch, get_summary_stats
from app.data_loader import load_reviews_from_csv
from app.emotion_analysis import analyze_emotion, analyze_emotion_detailed, analyze_emotion_ml
from app.firebase_service import push_analyzed_results, save_review_with_analysis
from app.models.review import build_analysis_response, normalize_review_payload
from app.sentiment_analysis import analyze_sentiment, analyze_sentiment_detailed
from app.security import clamp_top_k, resolve_project_csv_path, validate_text_input
from app.vectorizer import find_similar_reviews

legacy_routes = Blueprint("legacy", __name__)


def _resolve_mode(data):
    mode = data.get("mode", "simple")
    if mode not in ("simple", "detailed", "ml"):
        return None
    return mode


@legacy_routes.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(
        {
            "status": "operational",
            "services": {
                "sentiment_analyzer": "running",
                "emotion_analyzer": "running",
                "vectorizer": "running",
            },
            "compatibility": "csv-analyser + sentiment-analyser legacy routes",
        }
    )


@legacy_routes.route("/api/analyze-sentiment", methods=["POST"])
def legacy_analyze_sentiment():
    data = request.get_json() or {}
    try:
        review = normalize_review_payload(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    mode = _resolve_mode(data) or "simple"
    text = f"{review['review_title']} {review['text']}".strip()
    sentiment = analyze_sentiment_detailed(text) if mode in ("detailed", "ml") else analyze_sentiment(text)
    review_id, storage = save_review_with_analysis({**review, "sentiment": sentiment}, review["product_url"])
    return jsonify(build_analysis_response(review_id, sentiment=sentiment, storage=storage))


@legacy_routes.route("/api/analyze-emotion", methods=["POST"])
def legacy_analyze_emotion():
    data = request.get_json() or {}
    try:
        review = normalize_review_payload(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    mode = _resolve_mode(data) or "simple"
    text = f"{review['review_title']} {review['text']}".strip()
    if mode == "ml":
        emotion = analyze_emotion_ml(text)
    elif mode == "detailed":
        emotion = analyze_emotion_detailed(text)
    else:
        emotion = analyze_emotion(text)

    review_id, storage = save_review_with_analysis({**review, "emotion": emotion}, review["product_url"])
    return jsonify(build_analysis_response(review_id, emotion=emotion, storage=storage))


@legacy_routes.route("/api/parse-text", methods=["POST"])
def legacy_parse_text():
    data = request.get_json() or {}
    try:
        review = normalize_review_payload(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    mode = _resolve_mode(data) or "simple"
    analyzed = analyze_reviews_batch([review], mode=mode, include_vector=True)[0]
    review_id, storage = save_review_with_analysis(analyzed, review["product_url"])
    analyzed["review_id"] = review_id
    analyzed["storage"] = storage
    return jsonify(analyzed)


@legacy_routes.route("/api/parse-file", methods=["POST"])
def legacy_parse_file():
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    upload = request.files["file"]
    if not upload.filename or not upload.filename.lower().endswith(".csv"):
        return jsonify({"error": "File must be a CSV"}), 400

    mode = request.form.get("mode", "simple")
    include_vector = request.form.get("include_vector", "false").lower() == "true"
    push_to_firebase = request.form.get("push_to_firebase", "true").lower() == "true"

    reviews = load_reviews_from_csv(file_content=upload.read())
    results = analyze_reviews_batch(reviews, mode=mode, include_vector=include_vector)
    summary = get_summary_stats(results)

    response = {
        "total_reviews": len(results),
        "results": results,
        "summary": summary,
    }

    if push_to_firebase:
        response["firebase"] = push_analyzed_results(results)

    return jsonify(response)


@legacy_routes.route("/api/find-similar", methods=["POST"])
def legacy_find_similar():
    data = request.get_json(silent=True) or {}
    try:
        query_text = validate_text_input(data.get("text"))
        top_k = clamp_top_k(data.get("top_k", 5))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    reviews = data.get("reviews")
    if reviews is None:
        csv_path = data.get("csv_path", "sample_reviews.csv")
        try:
            safe_path = resolve_project_csv_path(csv_path)
            reviews = load_reviews_from_csv(file_path=str(safe_path))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    similar_reviews = find_similar_reviews(query_text, reviews, top_k=top_k)
    return jsonify({"similar_reviews": similar_reviews})


@legacy_routes.route("/api/scrape-reviews", methods=["POST"])
def legacy_scrape_reviews():
    """Node frontend compatibility route from sentiment-analyser."""
    from app.amazon_scraper import scrape_amazon_reviews
    from app.firebase_service import save_review_to_db
    from app.scraper import scrape_reviews

    data = request.get_json() or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        if "amazon." in url.lower():
            reviews = scrape_amazon_reviews(url)
            source = "amazon"
        else:
            reviews = scrape_reviews(url)
            source = "generic"

        if isinstance(reviews, dict) and "error" in reviews:
            return jsonify(reviews), 502

        response = save_review_to_db(url, reviews)
        return jsonify({**response, "source": source})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
