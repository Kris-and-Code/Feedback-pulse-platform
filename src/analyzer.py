from transformers import pipeline
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis", max_length=512, truncation=True)

    def analyze_reviews(self, reviews):
        """
        Analyzes sentiment of Amazon reviews
        """
        results = []
        for review in reviews:
            try:
                # Combine review title and content for better analysis
                full_text = f"{review['review_title']} {review['text']}"
                
                # Analyze sentiment with truncation
                sentiment = self.sentiment_analyzer(full_text, truncation=True, max_length=512)[0]
                
                # Clean and convert rating
                try:
                    rating = float(str(review['rating']).split('|')[0].strip())  # Take first value before '|'
                except (ValueError, TypeError):
                    rating = 0.0  # Default value if rating can't be converted
                
                results.append({
                    'review_title': review['review_title'],
                    'text': review['text'][:500] + '...' if len(review['text']) > 500 else review['text'],
                    'user_name': review['user_name'],
                    'rating': rating,
                    'sentiment': sentiment['label'],
                    'sentiment_score': float(sentiment['score'])
                })
            except Exception as e:
                print(f"Warning: Error analyzing review: {str(e)}")
                results.append({
                    'review_title': review['review_title'],
                    'text': review['text'][:500] + '...' if len(review['text']) > 500 else review['text'],
                    'user_name': review['user_name'],
                    'rating': 0.0,  # Default value
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