from src.analyzer import Analyzer
from src.data_loader import AmazonDataLoader
import json
import asyncio
import aiofiles

class ReviewAnalysisSystem:
    def __init__(self):
        """Initialize the system components"""
        self.loader = AmazonDataLoader()
        self.analyzer = Analyzer('firebase-key.json')

    async def analyze_reviews(self, file_path):
        """
        Analyze reviews from sample CSV asynchronously
        """
        try:
            print(f"Loading reviews from: {file_path}")
            
            # Load reviews asynchronously
            reviews = await self.loader.load_reviews_async(file_path)
            print(f"Loaded {len(reviews)} reviews")

            # Analyze sentiments
            analysis_results = await self.analyzer.analyze_reviews(reviews)
            
            # Get summary statistics
            summary = self.analyzer.get_summary_stats(analysis_results)
            
            # Push to Firebase
            self.analyzer.push_to_firebase(analysis_results)

            # Save local results
            results = {
                'analysis': analysis_results,
                'summary': summary
            }
            await self.save_results_to_json_async(results, 'analysis_results.json')

            return {
                'success': True,
                'total_reviews': len(reviews),
                'results': results
            }

        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def save_results_to_json_async(self, results, filename):
        """Save analysis results to JSON file asynchronously"""
        try:
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(results, indent=4, ensure_ascii=False))
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")

    async def process_single_review(self, review_data, product_url):
        """
        Process a single review through the analysis pipeline
        """
        try:
            # Store review and get ID
            firebase_review_id = await self.analyzer.process_review(review_data, product_url)
            print(f"Review stored with ID: {firebase_review_id}")
            
            # Run analyses concurrently
            sentiment_task = asyncio.create_task(
                self.analyzer.sentiment_review(firebase_review_id)
            )
            emotion_task = asyncio.create_task(
                self.analyzer.emotion_review(firebase_review_id)
            )
            
            # Wait for both analyses to complete
            sentiment_result, emotion_result = await asyncio.gather(
                sentiment_task, 
                emotion_task,
                return_exceptions=True
            )
            
            return {
                'review_id': firebase_review_id,
                'sentiment': sentiment_result if not isinstance(sentiment_result, Exception) else None,
                'emotion': emotion_result if not isinstance(emotion_result, Exception) else None
            }
            
        except Exception as e:
            print(f"Error processing review: {str(e)}")
            return {
                'error': str(e)
            }

async def main():
    # Initialize system
    system = ReviewAnalysisSystem()
    
    # Path to sample reviews dataset
    dataset_path = "sample_reviews.csv"
    
    print("Starting Review Analysis System...")
    result = await system.analyze_reviews(dataset_path)
    
    if result['success']:
        print("\nAnalysis completed successfully!")
        print(f"Total reviews processed: {result['total_reviews']}")
        print("\nSummary:")
        print(json.dumps(result['results']['summary'], indent=2))
    else:
        print("\nAnalysis failed:", result['error'])

if __name__ == "__main__":
    asyncio.run(main())