import requests
from bs4 import BeautifulSoup

from app.security import is_safe_http_url


def scrape_reviews(url):
    if not is_safe_http_url(url):
        return {"error": "Invalid or disallowed URL"}

    response = requests.get(url, timeout=30, allow_redirects=True)
    if response.status_code != 200:
        return {"error": "Failed to fetch the URL"}

    final_url = response.url
    if not is_safe_http_url(final_url):
        return {"error": "Redirect target is not allowed"}

    soup = BeautifulSoup(response.text, "html.parser")

    reviews = []
    for review_div in soup.select(".review-class"):
        review_text = review_div.get_text(strip=True)
        rating_element = review_div.select_one(".rating-class")
        review_rating = rating_element.get_text(strip=True) if rating_element else None
        reviews.append({"text": review_text, "rating": review_rating})

    return reviews
