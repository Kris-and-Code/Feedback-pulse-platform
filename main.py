from src.analyzer import SentimentAnalyzer
from src.data_loader import AmazonDataLoader
import json
from datetime import datetime

class ReviewAnalysisSystem:
    def __init__(self):
        """Initialize the system components"""
        self.loader = AmazonDataLoader()
        self.analyzer = SentimentAnalyzer()

    def analyze_amazon_reviews(self, file_path):
        """
        Analyze Amazon product reviews
        """
        try:
            print(f"Loading reviews from: {file_path}")
            
            # Load reviews
            reviews = self.loader.load_reviews(file_path)
            print(f"Loaded {len(reviews)} reviews")

            # Group reviews by product
            products = {}
            for review in reviews:
                product_id = review['product_id']
                if product_id not in products:
                    products[product_id] = {
                        'product_name': review['product_name'],
                        'reviews': []
                    }
                products[product_id]['reviews'].append(review)

            # Analyze each product's reviews
            results = {}
            for product_id, product_data in products.items():
                print(f"\nAnalyzing product: {product_data['product_name'][:50]}...")
                
                # Analyze sentiments
                analysis_results = self.analyzer.analyze_reviews(product_data['reviews'])
                
                # Get summary statistics
                summary = self.analyzer.get_summary_stats(analysis_results)
                
                # Store results
                results[product_id] = {
                    'product_name': product_data['product_name'],
                    'analysis': analysis_results,
                    'summary': summary
                }

            # Save final results
            self.save_results_to_json(results, 'analysis_results.json')

            return {
                'success': True,
                'total_products': len(products),
                'total_reviews': len(reviews),
                'results': results
            }

        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def save_results_to_json(self, results, filename):
        """Save analysis results to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")

def main():
    # Initialize system
    system = ReviewAnalysisSystem()
    
    # Path to your Amazon reviews dataset
    dataset_path = "data/amazon_reviews.csv"
    
    print("Starting Amazon Review Analysis System...")
    result = system.analyze_amazon_reviews(dataset_path)
    
    if result['success']:
        print("\nAnalysis completed successfully!")
        print(f"Analyzed {result['total_products']} products")
        print(f"Total reviews processed: {result['total_reviews']}")
        
        # Print summary for each product
        for product_id, data in result['results'].items():
            print(f"\nProduct: {data['product_name'][:50]}...")
            print(json.dumps(data['summary'], indent=2))
    else:
        print("\nAnalysis failed:", result['error'])

if __name__ == "__main__":
    main()