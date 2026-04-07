import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.data = None

    def load_csv(self, file_path):
        try:
            logger.info(f"Loading data from {file_path}")
            self.data = pd.read_csv(file_path)
            
            # Extract relevant columns and convert to list of dictionaries
            reviews = []
            for _, row in self.data.iterrows():
                # Skip rows with missing values
                if pd.isna(row['review_content']) or pd.isna(row['rating']):
                    continue
                    
                review = {
                    'product_id': str(row['product_id']),
                    'product_name': str(row['product_name']),
                    'review_text': str(row['review_content']),
                    'rating': float(row['rating']),
                    'user_name': str(row['user_name']) if not pd.isna(row['user_name']) else "Anonymous",
                    'review_title': str(row['review_title']) if not pd.isna(row['review_title']) else ""
                }
                reviews.append(review)
            
            logger.info(f"Loaded {len(reviews)} valid reviews")
            return reviews
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            raise Exception(f"Error loading CSV file: {str(e)}")

    def group_by_product(self, reviews):
        """
        Group reviews by product ID
        """
        product_reviews = {}
        
        for review in reviews:
            product_id = review['product_id']
            if product_id not in product_reviews:
                product_reviews[product_id] = {
                    'product_name': review['product_name'],
                    'reviews': []
                }
            product_reviews[product_id]['reviews'].append(review)
            
        return product_reviews