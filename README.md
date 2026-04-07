# Review Analysis API

A FastAPI-based web service that provides functionality for scraping, analyzing, and aggregating product reviews with sentiment and emotion analysis capabilities.

## Features

- Review scraping from e-commerce platforms
- Sentiment analysis of reviews
- Emotion analysis of reviews
- Cloud-based storage with Firebase
- RESTful API endpoints

## Tech Stack

- FastAPI (Python 3.7+)
- Firebase Cloud Firestore
- BeautifulSoup4
- HTTPX

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/review-analysis-api.git
cd review-analysis-api
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add required environment variables:
```env
PROJECT_NAME=Review Analysis API
VERSION=1.0.0
FIREBASE_CREDENTIALS=path/to/firebase-credentials.json
```

## Usage

1. Start the server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
   - OpenAPI documentation: `http://localhost:8000/docs`
   - ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

- `GET /`: Root endpoint with API information
- `POST /scrape-reviews`: Scrape reviews from provided URL
- `GET /sentiment-aggregates/{url}`: Get sentiment analysis aggregates
- `GET /emotion-aggregates/{url}`: Get emotion analysis aggregates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.