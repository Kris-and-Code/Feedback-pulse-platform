import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    def __init__(self):
        try:
            # Download required NLTK data
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('averaged_perceptron_tagger')
            
            # Initialize emotion lexicons
            self.emotion_lexicon = {
                'joy': ['happy', 'great', 'excellent', 'good', 'wonderful', 'amazing', 'fantastic', 'love', 'perfect'],
                'anger': ['angry', 'terrible', 'horrible', 'bad', 'worst', 'hate', 'awful', 'disappointed'],
                'satisfaction': ['satisfied', 'works', 'reliable', 'solid', 'worth', 'recommended', 'quality'],
                'disappointment': ['disappointed', 'waste', 'poor', 'broken', 'defective', 'issue', 'problem'],
                'neutral': ['okay', 'average', 'decent', 'fine', 'normal', 'standard']
            }
            
            self.stop_words = set(stopwords.words('english'))
            logger.info("Emotion analyzer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing emotion analyzer: {str(e)}")
            raise

    def analyze_emotion(self, text):
        """Analyze emotions in the given text"""
        try:
            # Convert to string if not already
            text = str(text)
            
            # Create TextBlob object
            blob = TextBlob(text)
            
            # Get sentiment polarity (-1 to 1)
            sentiment_score = blob.sentiment.polarity
            
            # Tokenize and clean text
            tokens = word_tokenize(text.lower())
            tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
            
            # Count emotion words
            emotion_counts = {emotion: 0 for emotion in self.emotion_lexicon.keys()}
            
            for token in tokens:
                for emotion, words in self.emotion_lexicon.items():
                    if token in words:
                        emotion_counts[emotion] += 1
            
            # Determine primary emotion
            max_emotion = max(emotion_counts.items(), key=lambda x: x[1])
            primary_emotion = max_emotion[0] if max_emotion[1] > 0 else 'neutral'
            
            # Calculate emotion intensity
            total_emotion_words = sum(emotion_counts.values())
            emotion_intensity = total_emotion_words / len(tokens) if tokens else 0
            
            # Get subjectivity (0 to 1)
            subjectivity = blob.sentiment.subjectivity
            
            return {
                'primary_emotion': primary_emotion,
                'emotion_counts': emotion_counts,
                'emotion_intensity': emotion_intensity,
                'sentiment_score': sentiment_score,
                'subjectivity': subjectivity,
                'detailed_analysis': {
                    'word_count': len(tokens),
                    'emotion_words': total_emotion_words,
                    'is_subjective': subjectivity > 0.5,
                    'is_strong_emotion': emotion_intensity > 0.1
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing emotions: {str(e)}")
            return {
                'primary_emotion': 'error',
                'emotion_counts': {},
                'emotion_intensity': 0,
                'sentiment_score': 0,
                'subjectivity': 0,
                'detailed_analysis': {}
            }

    def get_emotion_summary(self, reviews):
        """Generate emotion summary for multiple reviews"""
        try:
            total_reviews = len(reviews)
            if total_reviews == 0:
                return {}
                
            emotion_totals = {emotion: 0 for emotion in self.emotion_lexicon.keys()}
            avg_sentiment = 0
            avg_subjectivity = 0
            
            for review in reviews:
                analysis = self.analyze_emotion(review['review_text'])
                emotion_totals[analysis['primary_emotion']] += 1
                avg_sentiment += analysis['sentiment_score']
                avg_subjectivity += analysis['subjectivity']
            
            return {
                'emotion_distribution': {
                    emotion: count/total_reviews 
                    for emotion, count in emotion_totals.items()
                },
                'average_sentiment': avg_sentiment/total_reviews,
                'average_subjectivity': avg_subjectivity/total_reviews,
                'total_reviews': total_reviews
            }
            
        except Exception as e:
            logger.error(f"Error generating emotion summary: {str(e)}")
            return {}

def main():
    # Test the emotion analyzer
    analyzer = EmotionAnalyzer()
    
    test_reviews = [
        {'review_text': "This product is amazing! I love it so much."},
        {'review_text': "Terrible quality, very disappointed with the purchase."},
        {'review_text': "It's okay, works as expected but nothing special."}
    ]
    
    # Test individual analysis
    print("\nIndividual Analysis:")
    for review in test_reviews:
        analysis = analyzer.analyze_emotion(review['review_text'])
        print(f"\nReview: {review['review_text']}")
        print(f"Primary Emotion: {analysis['primary_emotion']}")
        print(f"Sentiment Score: {analysis['sentiment_score']:.2f}")
    
    # Test summary
    print("\nSummary Analysis:")
    summary = analyzer.get_emotion_summary(test_reviews)
    print(f"Emotion Distribution: {summary['emotion_distribution']}")
    print(f"Average Sentiment: {summary['average_sentiment']:.2f}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
