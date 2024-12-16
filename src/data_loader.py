import pandas as pd

class AmazonDataLoader:
    def __init__(self):
        pass

    def clean_rating(self, rating):
        """Clean rating value"""
        try:
            # Remove any text and split by delimiter
            clean_rating = str(rating).split('|')[0].strip()
            return float(clean_rating)
        except (ValueError, TypeError):
            return 0.0

    def load_reviews(self, file_path):
        """
        Load Amazon product reviews from CSV
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Extract relevant columns and convert to list of dictionaries
            reviews = []
            for _, row in df.iterrows():
                review = {
                    'product_id': row['product_id'],
                    'product_name': row['product_name'],
                    'text': str(row['review_content']),
                    'rating': self.clean_rating(row['rating']),
                    'user_name': str(row['user_name']),
                    'review_title': str(row['review_title'])
                }
                reviews.append(review)

            return reviews

        except Exception as e:
            raise Exception(f"Error loading reviews: {str(e)}")

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