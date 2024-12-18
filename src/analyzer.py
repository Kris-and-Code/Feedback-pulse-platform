import asyncio
from firebase_admin import credentials, firestore, initialize_app
from src.sentiment_analyzer import SentimentAnalyzer
from src.emotion_analyzer import EmotionAnalyzer

class Analyzer:
    def __init__(self, firebase_key=None):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        
        # Initialize Firebase
        if firebase_key:
            cred = credentials.Certificate(firebase_key)
            initialize_app(cred)
            self.db = firestore.client()
        else:
            self.db = None

    async def process_review(self, review_data, product_url):
        """Process a single review and store in Firebase"""
        if not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            # Create a new document in the reviews collection
            review_ref = self.db.collection('reviews').document()
            
            # Prepare review data for Firebase
            firebase_data = {
                'review_title': review_data['review_title'],
                'text': review_data['text'],
                'user_name': review_data['user_name'],
                'rating': float(review_data['rating']),
                'product_url': product_url,
                'created_at': firestore.SERVER_TIMESTAMP,
                'sentiment_status': 'pending',
                'emotion_status': 'pending'
            }
            
            # Store the review
            review_ref.set(firebase_data)
            print(f"Stored review with ID: {review_ref.id}")
            
            return review_ref.id
            
        except Exception as e:
            print(f"Error storing review: {str(e)}")
            raise e

    async def sentiment_review(self, review_id):
        """Analyze sentiment for a specific review"""
        if not self.db:
            raise Exception("Firebase not initialized")
            
        try:
            # Get review document
            review_doc = self.db.collection('reviews').document(review_id).get()
            if not review_doc.exists:
                raise Exception(f"Review {review_id} not found")
                
            # Extract review data
            review_data = review_doc.to_dict()
            
            # Perform sentiment analysis
            return await self.sentiment_analyzer.analyze_review(review_doc, review_data)
            
        except Exception as e:
            print(f"Error in sentiment analysis: {str(e)}")
            raise e

    async def emotion_review(self, review_id):
        """Analyze emotion for a specific review"""
        if not self.db:
            raise Exception("Firebase not initialized")
            
        try:
            # Get review document
            review_doc = self.db.collection('reviews').document(review_id).get()
            if not review_doc.exists:
                raise Exception(f"Review {review_id} not found")
                
            # Extract review data
            review_data = review_doc.to_dict()
            
            # Perform emotion analysis
            return await self.emotion_analyzer.analyze_review(review_doc, review_data)
            
        except Exception as e:
            print(f"Error in emotion analysis: {str(e)}")
            raise e

    def get_summary_stats(self, analysis_results):
        """Calculate summary statistics from analysis results"""
        if not analysis_results:
            return {}
            
        total_reviews = len(analysis_results)
        sentiment_counts = {}
        emotion_counts = {}
        avg_rating = 0
        
        for result in analysis_results:
            # Count sentiments
            sentiment = result['sentiment']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Count emotions
            emotion = result['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            # Sum ratings
            avg_rating += result['rating']
            
        return {
            'total_reviews': total_reviews,
            'average_rating': avg_rating / total_reviews if total_reviews > 0 else 0,
            'sentiment_distribution': {
                k: v/total_reviews for k, v in sentiment_counts.items()
            },
            'emotion_distribution': {
                k: v/total_reviews for k, v in emotion_counts.items()
            }
        }

    def push_to_firebase(self, analysis_results):
        """Push analysis results to Firebase"""
        if not self.db:
            raise Exception("Firebase not initialized")
            
        try:
            # Create a batch write
            batch = self.db.batch()
            
            # Add each result to the batch
            for result in analysis_results:
                doc_ref = self.db.collection('analyzed_reviews').document()
                batch.set(doc_ref, {
                    **result,
                    'created_at': firestore.SERVER_TIMESTAMP
                })
                
            # Commit the batch
            batch.commit()
            print(f"Successfully pushed {len(analysis_results)} results to Firebase")
            
        except Exception as e:
            print(f"Error pushing to Firebase: {str(e)}")
            raise e

    async def analyze_reviews(self, reviews):
        """
        Analyze multiple reviews and store results in Firebase
        """
        try:
            results = []
            for review in reviews:
                # Process each review and get its Firebase ID
                review_id = await self.process_review(review, review.get('product_url', 'N/A'))
                
                # Run sentiment and emotion analysis concurrently
                sentiment_task = asyncio.create_task(self.sentiment_review(review_id))
                emotion_task = asyncio.create_task(self.emotion_review(review_id))
                
                # Wait for both analyses to complete
                sentiment_result, emotion_result = await asyncio.gather(
                    sentiment_task, 
                    emotion_task,
                    return_exceptions=True
                )
                
                # Prepare analysis result
                analysis_result = {
                    'review_id': review_id,
                    'review_title': review['review_title'],
                    'text': review['text'],
                    'user_name': review['user_name'],
                    'rating': float(review['rating']),
                }
                
                # Add sentiment analysis results if successful
                if not isinstance(sentiment_result, Exception):
                    analysis_result.update({
                        'sentiment': sentiment_result['sentiment'],
                        'sentiment_score': sentiment_result['confidence']
                    })
                
                # Add emotion analysis results if successful
                if not isinstance(emotion_result, Exception):
                    analysis_result.update({
                        'emotion': emotion_result['primary_emotion']['label'],
                        'emotion_score': emotion_result['primary_emotion']['confidence']
                    })
                
                results.append(analysis_result)
                
            return results
            
        except Exception as e:
            print(f"Error analyzing reviews: {str(e)}")
            raise e
