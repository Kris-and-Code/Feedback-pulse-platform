from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from app.services.scraper import scraper_service
from app.services.database import firebase_service
from app.models.review import ReviewResponse, SentimentAggregates, EmotionAggregates
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Review Analysis API",
        "endpoints": {
            "scrape_reviews": "/scrape-reviews",
            "sentiment_aggregates": "/sentiment-aggregates/{url}",
            "emotion_aggregates": "/emotion-aggregates/{url}"
        }
    }

@app.post("/scrape-reviews", response_model=ReviewResponse)
async def scrape_reviews(url: str = Body(...)):
    try:
        review_ids = await scraper_service.scrape_reviews(url)
        return ReviewResponse(
            status="success",
            review_ids=review_ids,
            message=f"Successfully scraped {len(review_ids)} reviews"
        )
    except Exception as e:
        return ReviewResponse(
            status="error",
            review_ids=[],
            message=str(e)
        )

@app.get("/sentiment-aggregates/{url}", response_model=SentimentAggregates)
async def get_sentiment_aggregates(url: str):
    try:
        reviews_ref = firebase_service.db.collection('reviews').document(url).collection('review_items')
        reviews = reviews_ref.stream()
        
        sentiment_counts = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
        total_reviews = 0
        
        for review in reviews:
            review_data = review.to_dict()
            if 'sentiment' in review_data:
                sentiment_counts[review_data['sentiment']] += 1
                total_reviews += 1
        
        if total_reviews == 0:
            raise HTTPException(status_code=404, detail="No reviews found")
            
        return SentimentAggregates(
            POSITIVE=sentiment_counts['POSITIVE']/total_reviews,
            NEUTRAL=sentiment_counts['NEUTRAL']/total_reviews,
            NEGATIVE=sentiment_counts['NEGATIVE']/total_reviews
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/emotion-aggregates/{url}", response_model=EmotionAggregates)
async def get_emotion_aggregates(url: str):
    try:
        reviews_ref = firebase_service.db.collection('reviews').document(url).collection('review_items')
        reviews = reviews_ref.stream()
        
        emotion_counts = {'HAPPY': 0, 'SAD': 0, 'ANGRY': 0, 'NEUTRAL': 0}
        total_reviews = 0
        
        for review in reviews:
            review_data = review.to_dict()
            if 'emotion' in review_data:
                emotion_counts[review_data['emotion']] += 1
                total_reviews += 1
        
        if total_reviews == 0:
            raise HTTPException(status_code=404, detail="No reviews found")
            
        return EmotionAggregates(
            HAPPY=emotion_counts['HAPPY']/total_reviews,
            SAD=emotion_counts['SAD']/total_reviews,
            ANGRY=emotion_counts['ANGRY']/total_reviews,
            NEUTRAL=emotion_counts['NEUTRAL']/total_reviews
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 