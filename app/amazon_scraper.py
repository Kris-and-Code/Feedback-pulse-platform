import re
import time

import requests
from bs4 import BeautifulSoup

AMAZON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _extract_product_id(url):
    match = re.search(r"/dp/([A-Z0-9]{10})", url)
    if match:
        return match.group(1)
    match = re.search(r"/product-reviews/([A-Z0-9]{10})", url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Amazon product URL")


def _fetch_page(url, max_retries=3):
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=AMAZON_HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Failed to fetch Amazon page after {max_retries} attempts: {last_error}")


def _parse_review_element(review_element):
    review_id = review_element.get("id", "")

    title_element = review_element.find("a", {"data-hook": "review-title"})
    title = title_element.get_text(strip=True) if title_element else ""

    rating_element = review_element.find("i", {"data-hook": "review-star-rating"})
    rating = 0.0
    if rating_element:
        rating_text = rating_element.get_text()
        try:
            rating = float(rating_text.split(" out of")[0])
        except ValueError:
            rating = 0.0

    text_element = review_element.find("span", {"data-hook": "review-body"})
    review_text = text_element.get_text(strip=True) if text_element else ""

    date_element = review_element.find("span", {"data-hook": "review-date"})
    review_date = date_element.get_text(strip=True) if date_element else ""

    verified = bool(review_element.find("span", {"data-hook": "avp-badge"}))

    if not review_text:
        return None

    return {
        "review_id": review_id,
        "review_title": title,
        "title": title,
        "text": review_text,
        "rating": rating,
        "date": review_date,
        "verified_purchase": verified,
        "user_name": "Amazon User",
    }


def scrape_amazon_reviews(url):
    product_id = _extract_product_id(url)
    reviews_url = f"https://www.amazon.com/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm"
    content = _fetch_page(reviews_url)
    soup = BeautifulSoup(content, "html.parser")

    reviews = []
    for review_element in soup.find_all("div", {"data-hook": "review"}):
        review = _parse_review_element(review_element)
        if review:
            reviews.append(review)

    if not reviews:
        return {"error": "No Amazon reviews found. Amazon may be blocking automated requests."}

    return reviews
