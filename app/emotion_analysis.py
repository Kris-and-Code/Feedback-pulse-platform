EMOTION_LEXICON = {
    "joy": ["happy", "great", "excellent", "good", "wonderful", "amazing", "fantastic", "love", "perfect"],
    "anger": ["angry", "terrible", "horrible", "bad", "worst", "hate", "awful", "disappointed"],
    "satisfaction": ["satisfied", "works", "reliable", "solid", "worth", "recommended", "quality"],
    "disappointment": ["disappointed", "waste", "poor", "broken", "defective", "issue", "problem"],
    "neutral": ["okay", "average", "decent", "fine", "normal", "standard"],
}

_emotion_ml_analyzer = None


def _get_emotion_ml_analyzer():
    global _emotion_ml_analyzer
    if _emotion_ml_analyzer is None:
        from transformers import pipeline

        _emotion_ml_analyzer = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True,
        )
    return _emotion_ml_analyzer


def analyze_emotion(text):
    """Detect primary emotion using a lightweight keyword lexicon."""
    text_lower = str(text).lower()
    scores = {
        emotion: sum(1 for word in words if word in text_lower)
        for emotion, words in EMOTION_LEXICON.items()
    }

    primary_emotion, top_score = max(scores.items(), key=lambda item: item[1])
    if top_score == 0:
        return "neutral"
    return primary_emotion


def analyze_emotion_detailed(text):
    """Rich emotion analysis using TextBlob and the keyword lexicon."""
    from textblob import TextBlob

    text = str(text)
    blob = TextBlob(text)
    tokens = [word.lower() for word in blob.words if word.isalnum()]

    emotion_counts = {emotion: 0 for emotion in EMOTION_LEXICON}
    for token in tokens:
        for emotion, words in EMOTION_LEXICON.items():
            if token in words:
                emotion_counts[emotion] += 1

    primary_emotion = max(emotion_counts.items(), key=lambda item: item[1])
    total_emotion_words = sum(emotion_counts.values())
    emotion_intensity = total_emotion_words / len(tokens) if tokens else 0.0

    return {
        "primary_emotion": primary_emotion[0] if primary_emotion[1] > 0 else "neutral",
        "emotion_counts": emotion_counts,
        "emotion_intensity": emotion_intensity,
        "sentiment_score": blob.sentiment.polarity,
        "subjectivity": blob.sentiment.subjectivity,
    }


def analyze_emotion_ml(text):
    """Transformer-based emotion classification."""
    predictions = _get_emotion_ml_analyzer()(str(text))[0]
    sorted_predictions = sorted(predictions, key=lambda item: item["score"], reverse=True)
    primary = sorted_predictions[0]
    secondary = [item for item in sorted_predictions[1:] if item["score"] > 0.2]

    return {
        "primary_emotion": {
            "label": primary["label"],
            "confidence": float(primary["score"]),
        },
        "secondary_emotions": [
            {"label": item["label"], "confidence": float(item["score"])} for item in secondary
        ],
        "all_scores": [
            {"label": item["label"], "score": float(item["score"])} for item in predictions
        ],
    }


def aggregate_emotions(reviews):
    """Return emotion distribution for a list of review dicts."""
    if not reviews:
        return {}

    counts = {}
    for review in reviews:
        text = review.get("text") or review.get("review_text", "")
        emotion = analyze_emotion(text)
        counts[emotion] = counts.get(emotion, 0) + 1

    total = len(reviews)
    return {emotion: count / total for emotion, count in counts.items()}
