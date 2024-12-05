def analyze_emotion(text):
    emotions = {"happy": "happy", "sad": "sad", "angry": "angry", "neutral": "neutral"}
    for key in emotions:
        if key in text.lower():
            return emotions[key]
    return "neutral"
