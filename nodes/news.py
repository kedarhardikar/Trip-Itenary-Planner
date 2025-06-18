import requests
import os
from dotenv import load_dotenv

# Load your env keys (no input prompts inside chain nodes)
load_dotenv()
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def fetch_news(state: dict) -> dict:
    
    """
    Node to fetch latest news for the destination city.
    """
    city = state.get("location", {}).get("city", "")
    
    if not city:
        print("No city found in state")
        return state

    # You can modify the date range logic if needed
    from_date = "2025-06-01"
    to_date = "2024-06-03"

    url = (
        f"https://newsapi.org/v2/everything?q={city}&from={from_date}&sortBy=popularity&apiKey={NEWS_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        articles = []

        if data['articles']:
            for article in data['articles']:
                title = article.get("title", "No Title")
                published_at = article.get("publishedAt", "")
                url_link = article.get("url", "")
                
                articles.append({
                    "title": title,
                    "published_at": published_at,
                    "url": url_link
                })

            
            # Now print only the titles
            i = 0
            for i,article in enumerate(articles):
                
                print(article["title"])
                if i>10:
                     break

        else:
                print(" No articles found.")

        # ✅ Inject back into state
        return {
                **state,
                "city_news": articles
            }

    except Exception as e:
        print(f"News API call failed: {e}")
        return state
