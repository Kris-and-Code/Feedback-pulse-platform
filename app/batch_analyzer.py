from app.emotion_analysis import analyze_emotion, analyze_emotion_ml
from app.sentiment_analysis import analyze_sentiment, analyze_sentiment_detailed
from app.vectorizer import encode_text


def _review_text(review):
    return f"{review.get('review_title', '')} {review['text']}".strip()


def _normalize_sentiment(value):
    if isinstance(value, dict):
        return value.get("sentiment", "neutral")
    return value


def _normalize_emotion(value):
    if isinstance(value, dict):
        if "primary_emotion" in value:
            primary = value["primary_emotion"]
            if isinstance(primary, dict):
                return primary.get("label", "neutral")
            return primary
        return value.get("primary_emotion", "neutral")
    return value


def analyze_single_review(review, mode="simple", include_vector=False):
    text = _review_text(review)
    result = {
        **review,
        "review_id": review.get("id") or review.get("review_id"),
    }

    if mode == "ml":
        sentiment_detail = analyze_sentiment_detailed(text)
        emotion_detail = analyze_emotion_ml(text)
        result["sentiment"] = sentiment_detail["sentiment"]
        result["sentiment_score"] = sentiment_detail["confidence"]
        result["emotion"] = emotion_detail["primary_emotion"]["label"]
        result["emotion_score"] = emotion_detail["primary_emotion"]["confidence"]
        result["emotion_analysis"] = emotion_detail
    elif mode == "detailed":
        sentiment_detail = analyze_sentiment_detailed(text)
        from app.emotion_analysis import analyze_emotion_detailed

        emotion_detail = analyze_emotion_detailed(text)
        result["sentiment"] = sentiment_detail["sentiment"]
        result["sentiment_score"] = sentiment_detail["confidence"]
        result["emotion"] = emotion_detail["primary_emotion"]
        result["emotion_analysis"] = emotion_detail
    else:
        result["sentiment"] = analyze_sentiment(text)
        result["emotion"] = analyze_emotion(text)

    if include_vector:
        embedding = encode_text(text)
        result["embedding"] = embedding
        result["embedding_dimension"] = len(embedding)
        result["vectorization_status"] = "completed"

    return result


def analyze_reviews_batch(reviews, mode="simple", include_vector=False):
    return [analyze_single_review(review, mode=mode, include_vector=include_vector) for review in reviews]


def get_summary_stats(analysis_results):
    if not analysis_results:
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "sentiment_distribution": {},
            "emotion_distribution": {},
        }

    sentiment_counts = {}
    emotion_counts = {}
    rating_total = 0.0

    for result in analysis_results:
        sentiment = _normalize_sentiment(result.get("sentiment"))
        emotion = _normalize_emotion(result.get("emotion"))
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        rating_total += float(result.get("rating", 0))

    total = len(analysis_results)
    return {
        "total_reviews": total,
        "average_rating": rating_total / total,
        "sentiment_distribution": {key: value / total for key, value in sentiment_counts.items()},
        "emotion_distribution": {key: value / total for key, value in emotion_counts.items()},
    }
