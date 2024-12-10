from transformers import pipeline

# Initialize the sentiment analysis pipeline globally (outside function)
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def analyze_sentiment(text):
    """
    Analyze the sentiment of given text using a pre-trained BERT model.
    Returns: 'positive', 'negative', or 'neutral' based on the analysis.
    """
    try:
        # Get sentiment prediction
        result = sentiment_analyzer(text)[0]
        score = result['score']
        
        # Convert 5-class sentiment to simplified positive/negative/neutral
        if score >= 0.6:
            return "positive"
        elif score <= 0.4:
            return "negative"
        else:
            return "neutral"
            
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return "neutral"  # fallback response
