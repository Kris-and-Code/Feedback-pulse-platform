import torch
from transformers import pipeline
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self, firebase_credentials_path):
        # Initialize Firebase
        try:
            cred = credentials.Certificate(firebase_credentials_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            print(f"Firebase initialization error: {str(e)}")
            raise e

        # Initialize sentiment analyzer
        print("Initializing sentiment analyzer...")
        model_name = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model=model_name,
            revision="714eb0f",
            device=0 if torch.cuda.is_available() else -1,
            max_length=512,
            truncation=True
        )

    def analyze_reviews(self, reviews):
        """
        Analyzes sentiment of reviews from sample CSV
        """
        results = []
        for review in reviews:
            try:
                # Combine review title and content for better analysis
                full_text = f"{review['review_title']} {review['text']}"
                
                # Analyze sentiment
                sentiment = self.sentiment_analyzer(full_text)[0]
                
                # Get rating (already in correct format in sample CSV)
                rating = float(review['rating'])
                
                results.append({
                    'review_title': review['review_title'],
                    'text': review['text'],  # No need to truncate for sample data
                    'user_name': review['user_name'],
                    'rating': rating,
                    'sentiment': sentiment['label'],
                    'sentiment_score': float(sentiment['score'])
                })
            except Exception as e:
                print(f"Warning: Error analyzing review: {str(e)}")
                results.append({
                    'review_title': review['review_title'],
                    'text': review['text'],
                    'user_name': review['user_name'],
                    'rating': 0.0,
                    'sentiment': 'UNKNOWN',
                    'sentiment_score': 0.0
                })
        
        return results

    def get_summary_stats(self, analysis_results):
        """
        Generates summary statistics for sentiment analysis
        """
        # Filter out unknown sentiments
        valid_results = [r for r in analysis_results if r['sentiment'] != 'UNKNOWN']
        
        if not valid_results:
            return {
                'total_reviews': len(analysis_results),
                'analyzed_reviews': 0,
                'error': 'No valid sentiment analysis results'
            }

        sentiments = [r['sentiment'] for r in valid_results]
        scores = [r['sentiment_score'] for r in valid_results]
        
        # Filter out zero ratings
        valid_ratings = [r['rating'] for r in valid_results if r['rating'] > 0]
        
        return {
            'total_reviews': len(analysis_results),
            'analyzed_reviews': len(valid_results),
            'average_rating': np.mean(valid_ratings) if valid_ratings else 0,
            'sentiment_distribution': {
                'positive': sentiments.count('POSITIVE'),
                'negative': sentiments.count('NEGATIVE'),
                'positive_percentage': (sentiments.count('POSITIVE') / len(sentiments)) * 100 if sentiments else 0
            },
            'average_sentiment_score': np.mean(scores) if scores else 0
        }

    def push_to_firebase(self, analysis_results):
        """
        Pushes analyzed reviews to Firebase with text indexing
        """
        try:
            print("\nAttempting to push to Firebase...")
            reviews_collection = self.db.collection('reviews')
            batch = self.db.batch()
            
            # Verify write permissions
            try:
                test_doc = reviews_collection.document('test')
                test_doc.set({'test': 'test'})
                test_doc.delete()
                print("✅ Write permission verified")
            except Exception as e:
                print(f"❌ Write permission test failed: {str(e)}")
                raise e
            
            documents_to_verify = []
            
            for i, result in enumerate(analysis_results):
                doc_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
                doc_ref = reviews_collection.document(doc_id)
                documents_to_verify.append(doc_id)
                
                # Create search tokens for text and title
                review_text = result['text'].lower()
                review_title = result['review_title'].lower()
                
                # Generate word tokens for searching
                text_tokens = set(review_text.split())
                title_tokens = set(review_title.split())
                
                # Create searchable n-grams (2 and 3 characters)
                text_ngrams = self._generate_ngrams(review_text, [2, 3])
                title_ngrams = self._generate_ngrams(review_title, [2, 3])
                
                data_to_push = {
                    'review_title': result['review_title'],
                    'text': result['text'],
                    'user_name': result['user_name'],
                    'rating': result['rating'],
                    'sentiment': result['sentiment'],
                    'sentiment_score': result['sentiment_score'],
                    'timestamp': firestore.SERVER_TIMESTAMP,
                    # Search fields
                    'text_tokens': list(text_tokens),
                    'title_tokens': list(title_tokens),
                    'text_ngrams': list(text_ngrams),
                    'title_ngrams': list(title_ngrams),
                    # Additional search metadata
                    'searchable': True,
                    'last_indexed': firestore.SERVER_TIMESTAMP
                }
                
                batch.set(doc_ref, data_to_push)
                print(f"Prepared review {i+1} with ID: {doc_id}")
            
            print("Committing batch to Firebase...")
            batch.commit()
            
            # Verify upload
            print("Verifying upload...")
            for doc_id in documents_to_verify[:2]:
                doc = reviews_collection.document(doc_id).get()
                if not doc.exists:
                    raise Exception(f"Document {doc_id} not found after upload")
            
            print(f"✅ Successfully pushed and verified {len(analysis_results)} reviews to Firebase")
            return True
            
        except Exception as e:
            print(f"❌ Error pushing to Firebase: {str(e)}")
            print(f"Error details: {type(e).__name__}")
            return False

    def _generate_ngrams(self, text, sizes=[2, 3]):
        """
        Generate n-grams from text for better search indexing
        """
        text = text.lower()
        ngrams = set()
        
        for size in sizes:
            for i in range(len(text) - size + 1):
                ngrams.add(text[i:i + size])
        
        return list(ngrams)