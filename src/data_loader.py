import csv
from io import StringIO
import asyncio

class AmazonDataLoader:
    def __init__(self):
        pass

    async def load_reviews_async(self, file_path):
        """
        Load reviews from sample CSV using asyncio
        """
        try:
            print(f"Starting file read from {file_path}")
            reviews = []
            
            # Read CSV file using asyncio
            loop = asyncio.get_running_loop()
            content = await loop.run_in_executor(None, self._read_file, file_path)
            
            # Parse CSV content
            csv_reader = csv.DictReader(StringIO(content))
            for row in csv_reader:
                review = {
                    'review_title': str(row['review_title']),
                    'text': str(row['text']),
                    'user_name': str(row['user_name']),
                    'rating': float(row['rating'])
                }
                reviews.append(review)
                    
            print(f"Successfully loaded {len(reviews)} reviews")
            return reviews

        except Exception as e:
            print(f"Error in load: {str(e)}")
            raise Exception(f"Error loading reviews: {str(e)}")

    def _read_file(self, file_path):
        """Helper method to read file synchronously"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_product_stats(self, df):
        """
        Get basic statistics about products
        """
        stats = {
            'total_products': df['product_id'].nunique(),
            'total_reviews': len(df),
            'avg_rating': df['rating'].apply(self.clean_rating).mean(),
            'products': []
        }
        
        for product_id in df['product_id'].unique():
            product_df = df[df['product_id'] == product_id]
            stats['products'].append({
                'product_id': product_id,
                'product_name': product_df['product_name'].iloc[0],
                'review_count': len(product_df),
                'avg_rating': product_df['rating'].apply(self.clean_rating).mean()
            })
            
        return stats