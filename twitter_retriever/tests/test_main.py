import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import logging
import sys
import os

# Add project root to sys.path to allow direct import of twitter_retriever
# This assumes the tests are in twitter_retriever/tests and project root is one level above twitter_retriever
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import from twitter_retriever
# To run these tests, navigate to the project root directory and run:
# python -m unittest discover twitter_retriever/tests
# or
# python -m unittest twitter_retriever.tests.test_main
from twitter_retriever import main as twitter_main
from twitter_retriever import config as twitter_config

# Suppress logging during tests for cleaner output, unless specifically testing log messages
logging.disable(logging.CRITICAL)

class TestTwitterRetriever(unittest.TestCase):

    def test_parse_trends_from_soup_placeholder(self):
        # Test with placeholder HTML structure (spans)
        # NOTE: This test will need to be updated significantly once real selectors are known
        html_content = """
        <html><body>
            <span>This is a trend title over ten chars</span>
            <span>Short</span>
            <span>Another valid trend title example</span>
            <div><span>This is nested but still a trend</span></div>
            <span>This makes it eleven trends now.</span>
            <span>This makes it twelve trends now.</span>
            <span>This makes it thirteen trends now.</span>
            <span>This makes it fourteen trends now.</span>
            <span>This makes it fifteen trends now.</span>
            <span>This makes it sixteen trends now.</span>
            <span>This makes it seventeen trends now.</span>
            <span>This makes it eighteen trends now.</span>
        </body></html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        trends = twitter_main.parse_trends_from_soup(soup)
        # Current placeholder logic finds spans and has a limit of 10
        self.assertTrue(0 < len(trends) <= 10)
        if trends:
            self.assertIn("title", trends[0])
            self.assertIn("description", trends[0])
            self.assertEqual(trends[0]["title"], "This is a trend title over ten chars")

    def test_parse_trends_from_empty_soup(self):
        soup = BeautifulSoup("", 'html.parser')
        trends = twitter_main.parse_trends_from_soup(soup)
        self.assertEqual(len(trends), 0)

    @patch('twitter_retriever.main.requests.get')
    def test_scrape_x_trends_success(self, mock_requests_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><span>Trend 1</span></body></html>"
        mock_response.raise_for_status = MagicMock() # Mock this method
        mock_requests_get.return_value = mock_response

        soup = twitter_main.scrape_x_trends()
        self.assertIsNotNone(soup)
        mock_requests_get.assert_called_once_with(twitter_config.TRENDS_URL, headers=unittest.mock.ANY, timeout=10)

    @patch('twitter_retriever.main.requests.get')
    def test_scrape_x_trends_failure(self, mock_requests_get):
        mock_requests_get.side_effect = twitter_main.requests.exceptions.RequestException("Test network error")

        soup = twitter_main.scrape_x_trends()
        self.assertIsNone(soup)

    @patch('twitter_retriever.main.scrape_x_trends')
    def test_get_trending_events_scrape_mode(self, mock_scrape_x_trends):
        # Ensure config is set to SCRAPE for this test
        original_fetch_method = twitter_config.FETCH_METHOD
        twitter_config.FETCH_METHOD = "SCRAPE"

        # Mock the parsing function as well to isolate get_trending_events's logic
        with patch('twitter_retriever.main.parse_trends_from_soup') as mock_parse:
            mock_soup = MagicMock() # Simulate a BeautifulSoup object
            mock_scrape_x_trends.return_value = mock_soup
            mock_parse.return_value = [{"title": "Test Trend", "description": "Test Desc"}]

            events = twitter_main.get_trending_events()
            mock_scrape_x_trends.assert_called_once()
            mock_parse.assert_called_once_with(mock_soup)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["title"], "Test Trend")

        twitter_config.FETCH_METHOD = original_fetch_method # Reset config

    def test_get_trending_events_api_mode_placeholder(self):
        # Test current placeholder behavior for API mode
        original_fetch_method = twitter_config.FETCH_METHOD
        twitter_config.FETCH_METHOD = "API"
        events = twitter_main.get_trending_events()
        self.assertEqual(len(events), 0) # Current placeholder returns empty list
        twitter_config.FETCH_METHOD = original_fetch_method # Reset

    def test_get_trending_events_invalid_method(self):
        original_fetch_method = twitter_config.FETCH_METHOD
        twitter_config.FETCH_METHOD = "INVALID_METHOD"
        # This should log an error and return an empty list based on current implementation
        events = twitter_main.get_trending_events()
        self.assertEqual(len(events), 0)
        twitter_config.FETCH_METHOD = original_fetch_method # Reset

if __name__ == '__main__':
    # This allows running the tests directly from this file:
    # python twitter_retriever/tests/test_main.py
    # However, for discovery (e.g. from project root `python -m unittest discover ...`),
    # the sys.path manipulation at the top is more robust.
    unittest.main()
