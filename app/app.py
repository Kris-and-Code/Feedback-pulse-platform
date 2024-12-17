from app.services.scraper import ReviewScraper
from app.services.database import DatabaseManager
from app.services.analyzer import SentimentAnalyzer
from flask import Flask, request, jsonify

app = Flask(__name__)

scraper = ReviewScraper()
db_manager = DatabaseManager()
sentiment_analyzer = SentimentAnalyzer()

@app.route('/api/scrape', methods=['POST'])
def scrape_reviews():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Scrape reviews
        reviews = scraper.scrape_reviews(url)
        
        # Save to database
        doc_id = db_manager.save_reviews_to_db(url, reviews)
        
        # Perform sentiment analysis
        analysis_results = sentiment_analyzer.analyze_reviews(reviews)
        summary_stats = sentiment_analyzer.get_summary_stats(analysis_results)
        
        # Update database with sentiment analysis
        db_manager.update_review_sentiment(doc_id, {
            'analysis_results': analysis_results,
            'summary_stats': summary_stats
        })

        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'review_count': len(reviews),
            'sentiment_summary': summary_stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
