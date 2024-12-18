import torch
from transformers import pipeline
from firebase_admin import firestore

class EmotionAnalyzer:
    def __init__(self):
        print("Initializing emotion analyzer...")
        # Using a pre-trained emotion detection model
        self.model = pipeline(
            task="text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True,
            device=0 if torch.cuda.is_available() else -1
        )
        print(f"Emotion analyzer initialized. Using device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")

    async def analyze_review(self, review_doc, review_data):
        """
        Analyze emotions in a review using the pre-trained model
        """
        try:
            # Combine title and text for better context
            full_text = f"{review_data['review_title']} {review_data['text']}"
            
            # Get emotion predictions
            predictions = self.model(full_text)[0]
            
            # Sort emotions by confidence score
            sorted_emotions = sorted(predictions, key=lambda x: x['score'], reverse=True)
            
            # Get primary emotion (highest confidence)
            primary_emotion = sorted_emotions[0]
            
            # Get secondary emotions (confidence > 0.2)
            secondary_emotions = [
                emotion for emotion in sorted_emotions[1:]
                if emotion['score'] > 0.2
            ]

            # Prepare emotion analysis results
            emotion_analysis = {
                'primary_emotion': {
                    'label': primary_emotion['label'],
                    'confidence': float(primary_emotion['score'])
                },
                'secondary_emotions': [
                    {
                        'label': emotion['label'],
                        'confidence': float(emotion['score'])
                    }
                    for emotion in secondary_emotions
                ],
                'all_scores': [
                    {
                        'label': emotion['label'],
                        'score': float(emotion['score'])
                    }
                    for emotion in predictions
                ]
            }

            # Update the review document in Firebase
            update_data = {
                'emotion_analysis': emotion_analysis,
                'primary_emotion': emotion_analysis['primary_emotion']['label'],
                'emotion_confidence': emotion_analysis['primary_emotion']['confidence'],
                'emotion_status': 'completed',
                'last_updated': firestore.SERVER_TIMESTAMP
            }
            
            # Update Firebase document
            review_doc.reference.update(update_data)
            
            print(f"Emotion analysis completed for review {review_doc.id}")
            return emotion_analysis

        except Exception as e:
            error_msg = f"Error in emotion analysis: {str(e)}"
            print(error_msg)
            
            # Update review status to failed in Firebase
            review_doc.reference.update({
                'emotion_status': 'failed',
                'emotion_error': error_msg,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            raise e