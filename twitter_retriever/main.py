# Main script for Twitter Data Retriever

import config
import requests
from bs4 import BeautifulSoup
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import time # Will use for an initial execution
import json

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TREND_OUTPUT_FILE = "twitter_retriever/twitter_retriever_output.json"

def parse_trends_from_soup(soup):
    """Parses the BeautifulSoup object to extract trend data.
    IMPORTANT: The web scraping selectors below are placeholders and WILL require
    manual inspection of the X trending page's HTML and adjustment for the script
    to extract meaningful data. This initial version is unlikely to work correctly
    without updating these selectors.
    """
    logging.info("Attempting to parse trends from soup object.")
    extracted_trends = []
    try:
        # NOTE: The selectors below are placeholders and highly likely to change
        # based on X's actual HTML structure.
        # Example placeholder: trying to find spans, which is very generic.
        # Replace this with more specific selectors after inspecting X's HTML.
        trend_elements = soup.find_all('span') # This is a very generic placeholder

        for element in trend_elements:
            title = element.get_text(strip=True)
            # Add a basic filter: ignore very short or common navigation texts if possible
            if title and len(title) > 10: # Arbitrary length filter for placeholder
                description = "Description not available yet (selector needed)" # Placeholder
                extracted_trends.append({"title": title, "description": description})

            if len(extracted_trends) >= 10: # Limit the number of trends for this placeholder
                logging.info("Reached placeholder limit of 10 trends during parsing.")
                break

        logging.info(f"Found {len(extracted_trends)} potential trends after parsing.")
    except Exception as e:
        logging.error(f"Error during parsing trends from soup: {e}")
        return []
    return extracted_trends

def connect_to_x_api():
    """Connects to the X API using credentials from config.py.
    Note: Actual implementation will require an X API client library (e.g., Tweepy).
    """
    if config.FETCH_METHOD == "SCRAPE":
        logging.warning("API connection function called, but FETCH_METHOD is SCRAPE.")
    # Placeholder - actual implementation needed
    # logging.info(f"Connecting with API Key: {config.X_API_KEY[:5]}...")
    pass

def scrape_x_trends():
    """Scrapes trending topics from X."""
    logging.info(f"Attempting to scrape trends from: {config.TRENDS_URL}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(config.TRENDS_URL, headers=headers, timeout=10)
        response.raise_for_status()  # Check for HTTP errors
        logging.info(f"Successfully fetched content from {config.TRENDS_URL}")
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during requests to {config.TRENDS_URL}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during scraping: {e}")
        return None

def get_trending_events():
    """Fetches trending events based on the method specified in config.py."""
    if config.FETCH_METHOD == "API":
        logging.info("API method selected. Placeholder for API call.")
        # api = connect_to_x_api()
        # if api:
        #     # Fetch trends using the API
        #     # trends = api.get_place_trends(id=1)
        #     # return trends
        return []
    elif config.FETCH_METHOD == "SCRAPE":
        soup = scrape_x_trends()
        if soup:
            logging.info("Scraping successful, soup object created. Now parsing...")
            return parse_trends_from_soup(soup)
        else:
            logging.warning("Scraping failed or returned no content, so no parsing will be done.")
            return []
    else:
        logging.error(f"Invalid FETCH_METHOD '{config.FETCH_METHOD}' in config.py. Choose 'API' or 'SCRAPE'.")
        # Consider raising an error or returning empty list based on desired strictness
        return []


def fetch_and_log_trends():
    logging.info("Scheduler job: Initiating trend fetching...")
    events = get_trending_events()
    if events:
        logging.info(f"Scheduler job: Successfully fetched {len(events)} event(s).")
        try:
            with open(TREND_OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=4, ensure_ascii=False)
            logging.info(f"Scheduler job: Successfully saved {len(events)} events to {TREND_OUTPUT_FILE}")
        except IOError as e:
            logging.error(f"Scheduler job: Error saving events to {TREND_OUTPUT_FILE}: {e}")
        except Exception as e:
            logging.error(f"Scheduler job: Unexpected error while saving events to JSON: {e}")

        for i, event in enumerate(events): # Keep logging for console visibility
            logging.info(f"Scheduler job: Event {i+1} - Title: {event.get('title', 'N/A')}, Desc: {event.get('description', 'N/A')}")
    else:
        logging.info("Scheduler job: No trending events fetched or an error occurred during the process. No file will be saved.")

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="UTC") # Or your preferred timezone like 'Europe/London'

    # Run once on startup
    logging.info("Scheduler: Performing initial run of fetch_and_log_trends on startup.")
    fetch_and_log_trends()

    # Schedule job to run every 30 minutes
    scheduler.add_job(fetch_and_log_trends, 'interval', minutes=30)

    logging.info("Scheduler started. Trends will be fetched every 30 minutes. Press Ctrl+C to exit.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped by user.")
    except Exception as e:
        logging.error(f"Scheduler encountered an error: {e}")
    finally:
        if scheduler.running:
            scheduler.shutdown()
        logging.info("Scheduler shutdown complete.")
