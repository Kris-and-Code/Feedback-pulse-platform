import torch
from transformers import pipeline
from firebase_admin import firestore

class SentimentAnalyzer:
    def __init__(self):
        print("Initializing sentiment analyzer...")
        self.model = pipeline(
            "sentiment-analysis",
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            revision="714eb0f",
            device=0 if torch.cuda.is_available() else -1
        )

    async def analyze_review(self, review_doc, review_data):
        """
        Analyze sentiment of a specific review
        """
        try:
            # Combine title and text for analysis
            full_text = f"{review_data['review_title']} {review_data['text']}"
            
            # Perform sentiment analysis
            sentiment_result = self.model(full_text)[0]
            
            # Prepare sentiment analysis results
            sentiment_analysis = {
                'sentiment': sentiment_result['label'],
                'confidence': float(sentiment_result['score']),
                'rating': review_data['rating']
            }
            
            # Update the review document
            update_data = {
                'sentiment_analysis': sentiment_analysis,
                'sentiment': sentiment_result['label'],
                'sentiment_score': float(sentiment_result['score']),
                'sentiment_status': 'completed',
                'last_updated': firestore.SERVER_TIMESTAMP
            }
            
            # Update Firebase
            review_doc.reference.update(update_data)
            
            print(f"Sentiment analysis completed for review {review_doc.id}")
            return sentiment_analysis

        except Exception as e:
            error_msg = f"Error in sentiment analysis: {str(e)}"
            print(error_msg)
            # Update review status to failed
            review_doc.reference.update({
                'sentiment_status': 'failed',
                'sentiment_error': error_msg,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            raise e 