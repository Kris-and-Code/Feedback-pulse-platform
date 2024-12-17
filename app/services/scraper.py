import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from app.services.database import firebase_service
import re
from urllib.parse import urljoin

class ReviewScraper:
    BASE_URL = "https://www.amazon.com"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

    async def get_product_id(self, url: str) -> str:
        """Extract product ID from Amazon URL."""
        pattern = r'/dp/([A-Z0-9]{10})'
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Invalid Amazon product URL")
        return match.group(1)

    async def get_review_page(self, client: httpx.AsyncClient, url: str) -> str:
        """Fetch review page content with retry mechanism."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to fetch reviews after {max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    def parse_review(self, review_element: BeautifulSoup) -> Optional[Dict]:
        """Parse a single review element."""
        try:
            review_id = review_element.get('id', '')
            
            # Get review title
            title_element = review_element.find('a', {'data-hook': 'review-title'})
            title = title_element.get_text().strip() if title_element else ''
            
            # Get rating
            rating_element = review_element.find('i', {'data-hook': 'review-star-rating'})
            if rating_element:
                rating_text = rating_element.get_text()
                rating = float(rating_text.split(' out of')[0])
            else:
                rating = 0.0
            
            # Get review text
            text_element = review_element.find('span', {'data-hook': 'review-body'})
            review_text = text_element.get_text().strip() if text_element else ''
            
            # Get review date
            date_element = review_element.find('span', {'data-hook': 'review-date'})
            date = date_element.get_text().strip() if date_element else ''
            
            # Get verified purchase status
            verified = bool(review_element.find('span', {'data-hook': 'avp-badge'}))
            
            return {
                'review_id': review_id,
                'title': title,
                'rating': rating,
                'text': review_text,
                'date': date,
                'verified_purchase': verified
            }
        except Exception as e:
            print(f"Error parsing review: {str(e)}")
            return None

    async def scrape_reviews(self, url: str) -> List[str]:
        """Main method to scrape reviews."""
        product_id = await self.get_product_id(url)
        review_ids = []
        
        # Construct the reviews URL
        reviews_url = f"{self.BASE_URL}/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm"
        
        async with httpx.AsyncClient() as client:
            try:
                # Get the first page of reviews
                content = await self.get_review_page(client, reviews_url)
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find all review elements
                review_elements = soup.find_all('div', {'data-hook': 'review'})
                
                for review_element in review_elements:
                    review_data = self.parse_review(review_element)
                    if review_data:
                        # Store review in Firebase
                        doc_ref = (firebase_service.db
                                 .collection('reviews')
                                 .document(product_id)
                                 .collection('review_items')
                                 .document(review_data['review_id']))
                        
                        doc_ref.set(review_data)
                        review_ids.append(review_data['review_id'])
                
                return review_ids
                
            except Exception as e:
                raise Exception(f"Error scraping reviews: {str(e)}")

scraper_service = ReviewScraper()
