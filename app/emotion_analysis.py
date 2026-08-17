EMOTION_LEXICON = {
    "joy": ["happy", "great", "excellent", "good", "wonderful", "amazing", "fantastic", "love", "perfect"],
    "anger": ["angry", "terrible", "horrible", "bad", "worst", "hate", "awful", "disappointed"],
    "satisfaction": ["satisfied", "works", "reliable", "solid", "worth", "recommended", "quality"],
    "disappointment": ["disappointed", "waste", "poor", "broken", "defective", "issue", "problem"],
    "neutral": ["okay", "average", "decent", "fine", "normal", "standard"],
}


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
