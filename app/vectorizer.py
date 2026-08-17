import numpy as np

_vectorizer = None


def _get_vectorizer():
    global _vectorizer
    if _vectorizer is None:
        from sentence_transformers import SentenceTransformer

        _vectorizer = SentenceTransformer("all-MiniLM-L6-v2")
    return _vectorizer


def encode_text(text):
    embedding = _get_vectorizer().encode(str(text))
    return embedding.astype(float).tolist()


def _review_text(review):
    title = review.get("review_title") or review.get("title", "")
    body = review.get("text") or review.get("review_text", "")
    return f"{title} {body}".strip()


def find_similar_reviews(query_text, reviews, top_k=5):
    if not reviews:
        return []

    vectorizer = _get_vectorizer()
    query_embedding = vectorizer.encode(str(query_text))
    similarities = []

    for index, review in enumerate(reviews):
        review_text = _review_text(review)
        if not review_text:
            continue

        review_embedding = vectorizer.encode(review_text)
        similarity = float(
            np.dot(query_embedding, review_embedding)
            / (np.linalg.norm(query_embedding) * np.linalg.norm(review_embedding))
        )
        similarities.append(
            {
                "index": index,
                "similarity": similarity,
                "review": review,
            }
        )

    similarities.sort(key=lambda item: item["similarity"], reverse=True)
    return similarities[:top_k]
