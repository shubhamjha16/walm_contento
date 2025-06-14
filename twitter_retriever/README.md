# Twitter Data Retriever

## Overview

This component is responsible for fetching trending event data from X (formerly Twitter). It currently uses web scraping to gather trend titles and descriptions (though the description extraction is a placeholder). The fetched data is logged and saved to a temporary JSON file (`twitter_retriever_output.json`) in this directory. The fetching process is scheduled to run automatically every 30 minutes.

**IMPORTANT:** The web scraping logic, specifically the HTML selectors in `main.py`'s `parse_trends_from_soup()` function, uses placeholders. These **must** be inspected and adjusted based on the current HTML structure of X's trending page to extract meaningful data.

## Features

*   Fetches trending data from X via web scraping.
*   Schedules data fetching every 30 minutes (and once on startup).
*   Logs activities and fetched data to the console.
*   Saves the latest fetched trends to `twitter_retriever_output.json`.
*   Basic error handling for network requests and parsing.
*   Includes unit tests for key functionalities.

## Setup & Configuration

1.  **Python Version:** Python 3.7+ is recommended.
2.  **Install Dependencies:** Navigate to the project root directory and install the required packages:
    ```bash
    pip install -r twitter_retriever/requirements.txt
    ```
3.  **Configuration (`twitter_retriever/config.py`):**
    *   `FETCH_METHOD`: Set to `"SCRAPE"` for web scraping (current implementation) or `"API"` (placeholder, not implemented).
    *   `TRENDS_URL`: The URL for X's trending page if using scraping (defaults to a common one, but may need verification).
    *   `X_API_KEY`, `X_API_SECRET_KEY`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`: Placeholder API credentials. These are **not** used if `FETCH_METHOD` is `"SCRAPE"`.

4.  **Adjust Scraping Selectors (Crucial!):**
    *   Open `twitter_retriever/main.py`.
    *   Locate the `parse_trends_from_soup()` function.
    *   The HTML element selectors (e.g., `soup.find_all('span')`) are **placeholders**. You **must** inspect the live X trending page's HTML structure and update these selectors to accurately target the trend titles and descriptions. Failure to do so will result in incorrect or no data being extracted.

## How to Run

1.  **Navigate to the project's root directory.**
2.  **Execute the main script:**
    ```bash
    python -m twitter_retriever.main
    ```
    Alternatively, you can run `python twitter_retriever/main.py` if your `PYTHONPATH` is set up to include the project root, or if you are running it from within the `twitter_retriever` directory (though running as a module from root is often more robust for imports).

*   On startup, the script will perform an initial fetch and then continue to fetch trends every 30 minutes.
*   Logs will be printed to the console.
*   The latest trends will be saved in `twitter_retriever/twitter_retriever_output.json`.
*   Press `Ctrl+C` to stop the scheduler.

## How to Run Tests

1.  **Navigate to the project's root directory.**
2.  **Run the unit tests:**
    ```bash
    python -m unittest discover -s twitter_retriever/tests -p "test_*.py"
    ```
    Or, more simply if you are in the root and it's the only test discovery target:
    ```bash
    python -m unittest discover twitter_retriever/tests
    ```

## Dependencies

*   `requests`: For making HTTP requests.
*   `beautifulsoup4`: For parsing HTML content.
*   `APScheduler`: For scheduling the data fetching jobs.
