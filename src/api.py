from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from src.analyzer import Analyzer
from src.data_loader import AmazonDataLoader
import asyncio
import json

# Initialize FastAPI app
app = FastAPI(
    title="Review Analysis API",
    description="API for sentiment analysis, emotion detection, and text vectorization of reviews",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
analyzer = Analyzer('firebase-key.json')
data_loader = AmazonDataLoader()

@app.get("/")
async def root():
    """
    Root endpoint - provides API information and available endpoints
    """
    return {
        "name": "Review Analysis API",
        "version": "1.0.0",
        "description": "API for sentiment analysis, emotion detection, and text vectorization of reviews",
        "endpoints": {
            "sentiment_analysis": "/api/analyze-sentiment",
            "emotion_analysis": "/api/analyze-emotion",
            "parse_file": "/api/parse-file",
            "parse_text": "/api/parse-text",
            "find_similar": "/api/find-similar"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "services": {
            "sentiment_analyzer": "running",
            "emotion_analyzer": "running",
            "vectorizer": "running"
        }
    }

@app.get("/api/status")
async def api_status():
    """
    API status and configuration information
    """
    return {
        "status": "operational",
        "models": {
            "sentiment": {
                "name": "distilbert-base-uncased-finetuned-sst-2-english",
                "device": analyzer.sentiment_analyzer.device
            },
            "emotion": {
                "name": "emotion-english-distilroberta-base",
                "device": analyzer.emotion_analyzer.device
            },
            "vectorizer": {
                "name": "all-MiniLM-L6-v2",
                "device": analyzer.vectorizer.device
            }
        }
    }

# Pydantic models for request validation
class ReviewText(BaseModel):
    text: str
    title: Optional[str] = ""
    user_name: Optional[str] = "API_USER"
    rating: Optional[float] = 0.0

class SimilarityRequest(BaseModel):
    text: str
    top_k: Optional[int] = 5

class AnalysisResponse(BaseModel):
    review_id: str
    sentiment: Optional[dict] = None
    emotion: Optional[dict] = None

@app.post("/api/analyze-sentiment", response_model=AnalysisResponse)
async def analyze_sentiment(review: ReviewText):
    """
    Analyze sentiment of provided text
    
    Parameters:
    - text: Review text to analyze
    - title: Optional review title
    - user_name: Optional username
    - rating: Optional rating
    
    Returns:
    - review_id: Unique identifier for the review
    - sentiment: Sentiment analysis results
    """
    try:
        review_data = review.dict()
        
        # Process the review
        review_id = await analyzer.process_review(review_data, 'API_REQUEST')
        sentiment_result = await analyzer.sentiment_review(review_id)

        return {
            'review_id': review_id,
            'sentiment': sentiment_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-emotion", response_model=AnalysisResponse)
async def analyze_emotion(review: ReviewText):
    """
    Analyze emotions in provided text
    
    Parameters:
    - text: Review text to analyze
    - title: Optional review title
    - user_name: Optional username
    - rating: Optional rating
    
    Returns:
    - review_id: Unique identifier for the review
    - emotion: Emotion analysis results
    """
    try:
        review_data = review.dict()
        
        # Process the review
        review_id = await analyzer.process_review(review_data, 'API_REQUEST')
        emotion_result = await analyzer.emotion_review(review_id)

        return {
            'review_id': review_id,
            'emotion': emotion_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-file")
async def parse_file(file: UploadFile = File(...)):
    """
    Parse and analyze a CSV file of reviews
    
    Parameters:
    - file: CSV file upload
    
    Returns:
    - total_reviews: Number of reviews processed
    - results: Analysis results for each review
    - summary: Summary statistics
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        # Save the file temporarily
        content = await file.read()
        temp_path = 'temp_reviews.csv'
        with open(temp_path, 'wb') as f:
            f.write(content)

        # Load and analyze reviews
        reviews = await data_loader.load_reviews_async(temp_path)
        results = await analyzer.analyze_reviews(reviews)

        # Get summary statistics
        summary = analyzer.get_summary_stats(results)

        return {
            'total_reviews': len(reviews),
            'results': results,
            'summary': summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-text", response_model=AnalysisResponse)
async def parse_text(review: ReviewText):
    """
    Parse and analyze a single text review
    
    Parameters:
    - text: Review text to analyze
    - title: Optional review title
    - user_name: Optional username
    - rating: Optional rating
    
    Returns:
    - review_id: Unique identifier for the review
    - sentiment: Sentiment analysis results
    - emotion: Emotion analysis results
    """
    try:
        review_data = review.dict()
        
        # Process the review
        review_id = await analyzer.process_review(review_data, 'API_REQUEST')
        
        # Run all analyses concurrently
        sentiment_result, emotion_result = await asyncio.gather(
            analyzer.sentiment_review(review_id),
            analyzer.emotion_review(review_id)
        )

        return {
            'review_id': review_id,
            'sentiment': sentiment_result,
            'emotion': emotion_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/find-similar")
async def find_similar(request: SimilarityRequest):
    """
    Find similar reviews to the provided text
    
    Parameters:
    - text: Query text to find similar reviews
    - top_k: Number of similar reviews to return (default: 5)
    
    Returns:
    - similar_reviews: List of similar reviews with similarity scores
    """
    try:
        similar_reviews = await analyzer.vectorizer.find_similar_reviews(
            request.text,
            analyzer.db.collection('reviews'),
            top_k=request.top_k
        )

        return {
            'similar_reviews': similar_reviews
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 