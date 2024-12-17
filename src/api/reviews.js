// Reviews API service
export const scrapeReviews = async (url) => {
  try {
    const response = await fetch('/api/scrape-reviews', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error scraping reviews:', error);
    throw error;
  }
}; 