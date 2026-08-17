_sentiment_analyzer = None


def _get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        from transformers import pipeline

        _sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            revision="714eb0f",
        )
    return _sentiment_analyzer


def analyze_sentiment(text):
    """
    Analyze the sentiment of given text using a pre-trained model.
    Returns: 'positive', 'negative', or 'neutral'.
    """
    try:
        result = _get_sentiment_analyzer()(str(text))[0]
        label = result["label"].lower()
        if label in ("positive", "negative"):
            return label
        return "neutral"
    except Exception as exc:
        print(f"Error in sentiment analysis: {exc}")
        return "neutral"


def analyze_sentiment_detailed(text):
    """Return sentiment label and confidence score."""
    try:
        result = _get_sentiment_analyzer()(str(text))[0]
        return {
            "sentiment": result["label"].lower(),
            "confidence": float(result["score"]),
        }
    except Exception as exc:
        print(f"Error in sentiment analysis: {exc}")
        return {"sentiment": "neutral", "confidence": 0.0}


def aggregate_sentiments(reviews):
    """Return sentiment distribution for a list of review dicts."""
    if not reviews:
        return {}

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for review in reviews:
        text = review.get("text") or review.get("review_text", "")
        sentiment = analyze_sentiment(text)
        counts[sentiment] = counts.get(sentiment, 0) + 1

    total = len(reviews)
    return {sentiment: count / total for sentiment, count in counts.items()}
