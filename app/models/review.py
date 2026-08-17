def normalize_review_payload(data):
    """Normalize review input from any branch's API format."""
    text = data.get("text") or data.get("review_text") or data.get("review_content")
    if not text:
        raise ValueError("Review text is required")

    rating_raw = data.get("rating", 0)
    try:
        rating = float(rating_raw)
    except (TypeError, ValueError):
        rating = 0.0

    return {
        "review_title": str(data.get("review_title") or data.get("title", "")),
        "text": str(text),
        "user_name": str(data.get("user_name", "API_USER")),
        "rating": rating,
        "product_url": str(data.get("product_url", data.get("url", "API_REQUEST"))),
    }


def build_analysis_response(review_id, sentiment=None, emotion=None, storage=None):
    response = {"review_id": review_id}
    if sentiment is not None:
        response["sentiment"] = sentiment
    if emotion is not None:
        response["emotion"] = emotion
    if storage is not None:
        response["storage"] = storage
    return response
