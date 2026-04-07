from transformers import pipeline
from app.config import Config
from app.services.database import firebase_service

class AnalyzerService:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis", model=Config.MODEL_PATH_SENTIMENT)
        self.emotion_analyzer = pipeline("text-classification", model=Config.MODEL_PATH_EMOTION)

    async def analyze_sentiment(self, id: str):
        review_data = await firebase_service.get_review(id)
        sentiment_result = self.sentiment_analyzer(review_data['text'])[0]
        await firebase_service.update_review(id, {
            'sentiment': sentiment_result['label'],
            'sentiment_score': sentiment_result['score']
        })
        return sentiment_result

    async def analyze_emotion(self, id: str):
        review_data = await firebase_service.get_review(id)
        emotion_result = self.emotion_analyzer(review_data['text'])[0]
        await firebase_service.update_review(id, {
            'emotion': emotion_result['label'],
            'emotion_score': emotion_result['score']
        })
        return emotion_result

analyzer_service = AnalyzerService()