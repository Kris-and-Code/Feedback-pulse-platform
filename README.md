# Feedback Pulse Platform

Unified Flask API combining features from all branches: web scraping, Amazon scraping, CSV analysis, sentiment/emotion detection, vector similarity search, local SQLite storage, and optional Firebase persistence.

## Features

- Generic web scraper and Amazon-specific scraper
- Sentiment analysis (DistilBERT) with simple, detailed, and ML modes
- Emotion detection (lexicon, TextBlob detailed, transformer ML)
- CSV batch analysis
- Vector similarity search (`sentence-transformers`)
- Local SQLite feedback storage
- Firebase Firestore persistence (optional)
- Lazy-loaded models — server starts quickly

## Project Structure

```
Feedback-pulse-platform/
├── app/
│   ├── routes.py
│   ├── scraper.py
│   ├── amazon_scraper.py      # from sentiment-analyser
│   ├── firebase_service.py
│   ├── data_loader.py         # from csv-analyser
│   ├── vectorizer.py          # from csv-analyser
│   ├── local_db.py            # from sentiment-analyser
│   ├── sentiment_analysis.py
│   └── emotion_analysis.py
├── data/
│   └── amazon_reviews.csv
├── sample_reviews.csv
├── app.py
└── requirements.txt
```

## Branch Features Integrated

| Branch | Integrated into dev |
|--------|---------------------|
| `dev` | Flask API, generic scraper, Firebase |
| `csv-analyser` | CSV loader, vector similarity, DistilBERT sentiment, transformer emotion |
| `sentiment-analyser` | Amazon scraper, TextBlob emotion analysis, SQLite feedback DB |

## Installation

```bash
git clone https://github.com/Kris-and-Code/Feedback-pulse-platform.git
cd Feedback-pulse-platform
git checkout dev
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # optional Firebase setup
python app.py
```

API: `http://127.0.0.1:5000/`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/scrape-review` | Scrape generic URL |
| POST | `/scrape-amazon` | Scrape Amazon product reviews |
| POST | `/analyze-text` | Analyze text (`mode`: simple, detailed, ml) |
| POST | `/analyze-csv` | Upload CSV for batch analysis |
| POST | `/find-similar` | Find similar reviews by text embedding |
| POST | `/vectorize` | Get text embedding vector |
| GET/POST | `/feedback` | Local SQLite feedback storage |
| GET | `/aggregate-sentiment?url=` | Aggregate stored review sentiment |
| GET | `/aggregate-emotion?url=` | Aggregate stored review emotion |

### Analyze modes

- `simple` — fast lexicon emotion + basic sentiment label
- `detailed` — sentiment confidence + TextBlob emotion breakdown
- `ml` — transformer sentiment + transformer emotion classification

### Examples

```bash
# Analyze text
curl -X POST http://127.0.0.1:5000/analyze-text -H "Content-Type: application/json" -d "{\"text\":\"I love this product!\",\"mode\":\"detailed\"}"

# Analyze CSV
curl -X POST -F "file=@sample_reviews.csv" -F "mode=simple" http://127.0.0.1:5000/analyze-csv

# Find similar reviews
curl -X POST http://127.0.0.1:5000/find-similar -H "Content-Type: application/json" -d "{\"text\":\"great quality product\",\"top_k\":3}"

# Store feedback locally
curl -X POST http://127.0.0.1:5000/feedback -H "Content-Type: application/json" -d "{\"review_text\":\"Amazing product\",\"rating\":5}"
```

## Firebase (Optional)

Place `firebase-credentials.json` in the project root or set `FIREBASE_CREDENTIALS_PATH` in `.env`.

Use `FIREBASE_COLLECTION=feedback_pulse_v2` to store data in a separate Firestore collection from legacy data.

## Notes

- First `/analyze-text` or `/find-similar` call downloads ML models (may take time).
- Amazon scraping may be blocked by Amazon's bot protection.
- SQLite feedback is stored in `data/feedback.db` (gitignored).
