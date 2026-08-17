# Feedback Pulse Platform

Flask API for scraping product reviews, analyzing sentiment and emotion, and storing results in Firebase.

## Features

- Scrape reviews from a web page
- Perform sentiment analysis on review text
- Detect emotions in reviews
- Store and retrieve review data with Firebase Firestore

## Project Structure

```
Feedback-pulse-platform/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── scraper.py
│   ├── firebase_service.py
│   ├── sentiment_analysis.py
│   └── emotion_analysis.py
├── app.py
├── requirements.txt
├── .env
└── README.md
```

## Requirements

- Python 3.8+
- Firebase project with Firestore enabled

## Installation

1. Clone the repository:

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

4. Configure Firebase credentials in a `.env` file:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR-PRIVATE-KEY\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=your-client-email@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-client-email%40your-project-id.iam.gserviceaccount.com
```

5. Run the application:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000/`.

## API Endpoints

### Root

- **URL:** `/`
- **Method:** `GET`

### Scrape Reviews

- **URL:** `/scrape-review`
- **Method:** `POST`
- **Body:**

```json
{
  "url": "https://example.com"
}
```

### Aggregate Sentiment

- **URL:** `/aggregate-sentiment?url=https://example.com`
- **Method:** `GET`

### Aggregate Emotion

- **URL:** `/aggregate-emotion?url=https://example.com`
- **Method:** `GET`

## Branches

- `dev` — Flask API with Firebase integration
- `csv-analyser` — CSV-based review analysis tool
- `sentiment-analyser` — Extended sentiment analysis application

## Development Notes

- Update CSS selectors in `app/scraper.py` for the target review site.
- Sentiment analysis uses a Hugging Face transformer model and may download weights on first run.
- Emotion detection is a simple keyword-based placeholder and can be replaced with an NLP model.
