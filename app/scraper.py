import requests
from bs4 import BeautifulSoup


def scrape_reviews(url):
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        return {"error": "Failed to fetch the URL"}

    soup = BeautifulSoup(response.text, "html.parser")

    reviews = []
    for review_div in soup.select(".review-class"):
        review_text = review_div.get_text(strip=True)
        rating_element = review_div.select_one(".rating-class")
        review_rating = rating_element.get_text(strip=True) if rating_element else None
        reviews.append({"text": review_text, "rating": review_rating})

    return reviews
