# Feedback Pulse Platform

Unified Flask API for scraping product reviews, analyzing CSV/text feedback, and optionally storing results in Firebase.

## Features

- Scrape reviews from a web page (generic HTML selectors)
- Analyze sentiment and emotion for single text or CSV uploads
- Aggregate sentiment/emotion for stored reviews by URL
- Lazy-load transformer models (server starts without downloading weights)
- In-memory storage fallback when Firebase credentials are not configured

## Project Structure

```
Feedback-pulse-platform/
├── app/
│   ├── __init__.py
│   ├── routes.py              # Flask API endpoints
│   ├── scraper.py             # Web scraper (from dev)
│   ├── firebase_service.py    # Firebase + in-memory fallback
│   ├── data_loader.py         # CSV loader (from csv-analyser)
│   ├── sentiment_analysis.py  # Lazy-loaded transformers sentiment
│   └── emotion_analysis.py    # Lexicon-based emotion detection
├── app.py                     # Entry point
├── sample_reviews.csv         # Demo CSV data (from csv-analyser)
├── requirements.txt
├── .env.example
└── README.md
```

## Branches Merged

| Branch | What was integrated |
|--------|---------------------|
| `dev` | Flask app structure, scraper, Firebase routes |
| `csv-analyser` | CSV loading, batch analysis, `sample_reviews.csv` |
| `sentiment-analyser` | Emotion lexicon, in-memory DB fallback pattern, distilbert model choice |

## Requirements

- Python 3.8+
- Firebase project (optional — only needed for persistent cloud storage)

## Installation

1. Clone and checkout dev:

```bash
git clone https://github.com/Kris-and-Code/Feedback-pulse-platform.git
cd Feedback-pulse-platform
git checkout dev
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) Copy environment template and add Firebase credentials:

```bash
copy .env.example .env
```

The app runs without a `.env` file. Reviews are stored in memory until the process restarts.

5. Run the application:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000/`.

## API Endpoints

### Root

- **URL:** `/`
- **Method:** `GET`
- Returns API info and available endpoints.

### Health

- **URL:** `/health`
- **Method:** `GET`

### Scrape Reviews

- **URL:** `/scrape-review`
- **Method:** `POST`
- **Body:** `{ "url": "https://example.com" }`
- Saves scraped reviews to Firebase (if configured) or in-memory store.

### Analyze Text

- **URL:** `/analyze-text`
- **Method:** `POST`
- **Body:** `{ "text": "This product is amazing!" }`
- Downloads the sentiment model on first use.

### Analyze CSV

- **URL:** `/analyze-csv`
- **Method:** `POST`
- **Body:** multipart form with field `file` (CSV)
- Expected columns: `review_title`, `text`, `user_name`, `rating`

Example with curl:

```bash
curl -X POST -F "file=@sample_reviews.csv" http://127.0.0.1:5000/analyze-csv
```

### Aggregate Sentiment / Emotion

- **URL:** `/aggregate-sentiment?url=<url>` or `/aggregate-emotion?url=<url>`
- **Method:** `GET`
- Requires reviews previously stored via `/scrape-review`.

## Optional: Firebase

Set the variables in `.env.example` to enable Firestore persistence. Without them:

- `/scrape-review` stores reviews in an in-memory dict
- Aggregate endpoints work against in-memory data for the current process
- Data is lost when the server restarts

## Development Notes

- Update CSS selectors in `app/scraper.py` for your target review site.
- Sentiment analysis uses Hugging Face `distilbert-base-uncased-finetuned-sst-2-english` and downloads weights on first `/analyze-text` or `/analyze-csv` call.
- Emotion detection uses a lightweight keyword lexicon (no extra model download).
