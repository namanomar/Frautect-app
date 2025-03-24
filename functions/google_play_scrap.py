from google_play_scraper import app, reviews, Sort
from google_play_scraper.exceptions import NotFoundError

def get_play_store_data(app_id):
    try:
        app_details = app(app_id)
    except Exception as e:  
        print(f"Error fetching app details for {app_id}: {e}")
        app_details = {
            "title": "Not Found",
            "developer": "Unknown",
            "permissions": "Not Available",
            "description": "No description available"
        }

    try:
        review_data, _ = reviews(app_id, lang="en", country="inr", count=100, sort=Sort.NEWEST)
    except Exception as e:
        print(f"Error fetching reviews for {app_id}: {e}")
        review_data = []

    return app_details, review_data
