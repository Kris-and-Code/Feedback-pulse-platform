from src.analyzer import SentimentAnalyzer
from src.data_loader import AmazonDataLoader
import json
import asyncio
import aiofiles

class ReviewAnalysisSystem:
    def __init__(self):
        """Initialize the system components"""
        self.loader = AmazonDataLoader()
        self.analyzer = SentimentAnalyzer('firebase-key.json')

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
            analysis_results = self.analyzer.analyze_reviews(reviews)
            
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