from sentence_transformers import SentenceTransformer
import torch
from firebase_admin import firestore
import numpy as np

class ReviewVectorizer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the vectorizer with a pre-trained model
        Default model is all-MiniLM-L6-v2 which provides a good balance of speed and accuracy
        """
        print("Initializing text vectorizer...")
        self.model = SentenceTransformer(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        print(f"Vectorizer initialized. Using device: {self.device}")

    async def vectorize_review(self, review_doc, review_data):
        """
        Generate embeddings for a review and store in Firebase
        """
        try:
            # Combine title and text for a complete representation
            full_text = f"{review_data['review_title']} {review_data['text']}"
            
            # Generate embedding
            embedding = self.model.encode(full_text)
            
            # Convert to float32 for Firebase storage
            embedding_list = embedding.astype(float).tolist()
            
            # Update the review document with the embedding
            update_data = {
                'embedding': embedding_list,
                'embedding_dimension': len(embedding_list),
                'vectorization_status': 'completed',
                'last_updated': firestore.SERVER_TIMESTAMP
            }
            
            # Update Firebase document
            review_doc.reference.update(update_data)
            
            print(f"Vectorization completed for review {review_doc.id}")
            return {
                'embedding': embedding_list,
                'dimension': len(embedding_list)
            }

        except Exception as e:
            error_msg = f"Error in vectorization: {str(e)}"
            print(error_msg)
            
            # Update review status to failed in Firebase
            review_doc.reference.update({
                'vectorization_status': 'failed',
                'vectorization_error': error_msg,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            raise e

    async def find_similar_reviews(self, query_text, collection_ref, top_k=5):
        """
        Find similar reviews using cosine similarity
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query_text)
            
            # Get all reviews with embeddings
            reviews = collection_ref.where('vectorization_status', '==', 'completed').get()
            
            similarities = []
            for review in reviews:
                review_data = review.to_dict()
                if 'embedding' in review_data:
                    # Calculate cosine similarity
                    review_embedding = np.array(review_data['embedding'])
                    similarity = np.dot(query_embedding, review_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(review_embedding)
                    )
                    
                    similarities.append({
                        'review_id': review.id,
                        'similarity': float(similarity),
                        'review_data': review_data
                    })
            
            # Sort by similarity and get top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]

        except Exception as e:
            print(f"Error finding similar reviews: {str(e)}")
            raise e

    def batch_vectorize_reviews(self, reviews, batch_size=32):
        """
        Vectorize multiple reviews efficiently in batches
        """
        try:
            texts = [f"{review['review_title']} {review['text']}" for review in reviews]
            embeddings = []
            
            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(batch_texts)
                embeddings.extend(batch_embeddings)
            
            return embeddings

        except Exception as e:
            print(f"Error in batch vectorization: {str(e)}")
            raise e

    @staticmethod
    def create_vector_index(db):
        """
        Create a vector search index in Firebase
        Note: Requires Firebase Enterprise plan for vector search
        """
        try:
            collection_ref = db.collection('reviews')
            
            # Define the vector search index
            index = {
                'name': 'reviews_vector_index',
                'queryScope': 'COLLECTION',
                'fields': [{
                    'fieldPath': 'embedding',
                    'dimensions': 384,  # Dimension of all-MiniLM-L6-v2 embeddings
                    'vectorSearchConfiguration': 'reviews_vector_config'
                }]
            }
            
            # Create the index
            collection_ref.create_index(index)
            print("Vector search index created successfully")
            
        except Exception as e:
            print(f"Error creating vector index: {str(e)}")
            raise e 