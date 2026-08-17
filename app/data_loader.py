import csv
from io import StringIO


def load_reviews_from_csv(file_path=None, file_content=None):
    """
    Load reviews from a CSV file path or uploaded file content.

    Expected columns: review_title, text (or review_content), user_name, rating
    """
    if not file_path and not file_content:
        raise ValueError("Either file_path or file_content is required")

    if file_path:
        with open(file_path, "r", encoding="utf-8") as handle:
            content = handle.read()
    else:
        content = file_content.decode("utf-8") if isinstance(file_content, bytes) else file_content

    reviews = []
    reader = csv.DictReader(StringIO(content))
    for row in reader:
        text = row.get("text") or row.get("review_content") or row.get("review_text")
        if not text:
            continue

        rating_raw = row.get("rating", 0)
        try:
            rating = float(rating_raw)
        except (TypeError, ValueError):
            rating = 0.0

        reviews.append(
            {
                "review_title": str(row.get("review_title", "")),
                "text": str(text),
                "user_name": str(row.get("user_name", "Anonymous")),
                "rating": rating,
            }
        )

    return reviews
