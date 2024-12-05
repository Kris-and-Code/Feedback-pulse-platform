import requests
from bs4 import BeautifulSoup

def scrape_reviews(url):
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to fetch the URL"}

    soup = BeautifulSoup(response.text, 'html.parser')

    reviews = []
    # Adjust the selectors below to match the review HTML structure
    for review_div in soup.select('.review-class'):  # Replace .review-class with the correct selector
        review_text = review_div.get_text(strip=True)
        review_rating = review_div.select_one('.rating-class').get_text(strip=True)
        reviews.append({"text": review_text, "rating": review_rating})

    return reviews
