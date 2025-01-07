import unittest
from unittest.mock import patch, MagicMock
from functions import scraping
import requests
import logging

class TestScrapingFunctions(unittest.TestCase):

    @patch('functions.scraping.requests.get')  
    def test_meta_scraping_success(self, mock_get):
        # Simulate a successful HTML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html><head><title>Test Page</title></head><body></body></html>'
        mock_get.return_value = mock_response

        result = scraping.meta_scraping("http://example.com")
        self.assertEqual(result['Title'], "Test Page")

    @patch('functions.scraping.requests.get')  
    def test_meta_scraping_failure(self, mock_get):
        # Simulate a failed HTTP request
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = scraping.meta_scraping("http://example.com")
        self.assertIsNone(result)

    @patch('functions.scraping.fitz.open')
    def test_pdf_to_text(self, mock_open):
        # Mock un document PDF
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text from PDF."
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.page_count = 1
        mock_open.return_value.__enter__.return_value = mock_doc  # Fix: Properly mock __enter__

        result = scraping.pdf_to_text("sample.pdf")
        self.assertEqual(result, "Sample text from PDF.")

    @patch('functions.scraping.fitz.open')
    def test_pdf_meta_scraping(self, mock_open):
        # Mock les métadonnées d'un PDF
        mock_doc = MagicMock()
        mock_doc.metadata = {"title": "Sample PDF", "author": "John Doe", "creationDate": "D:20211212120000"}
        mock_open.return_value.__enter__.return_value = mock_doc  # Fix: Properly mock __enter__

        result = scraping.pdf_meta_scraping("sample.pdf")
        self.assertEqual(result["Title"], "Sample PDF")
        self.assertEqual(result["Author"], "John Doe")
        self.assertEqual(result["Creation Date"], "D:20211212120000")

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.remove')  
    @patch('functions.scraping.requests.get')
    @patch('functions.scraping.search')  
    @patch('functions.scraping.contains_keywords')
    @patch('functions.scraping.pdf_to_text')
    @patch('functions.scraping.pdf_meta_scraping')
    @patch('functions.scraping.meta_scraping')
    def test_scrape_webpages_to_db_html(self, mock_meta_scraping, mock_pdf_meta_scraping, mock_pdf_to_text, mock_contains_keywords, mock_search, mock_requests_get, mock_os_remove, mock_open):
        # Mock MongoDB collection
        mock_collection = MagicMock()

        # Ensure `find_one` always returns None, simulating a new URL
        mock_collection.find_one.side_effect = lambda query: None

        # Mock input data
        keywords_list = [
            ("test combined keyword", "test vocab", "test location")
        ]

        # Mock search results
        mock_search.return_value = ["http://example.com/test1.html"]

        # Mock requests.get

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_response.text = "<html><p>Test content including test vocab.</p></html>"
        mock_requests_get.return_value = mock_response

        # Mock contains_keywords
        mock_contains_keywords.return_value = True

        # Mock meta scraping
        mock_meta_scraping.return_value = {"meta_key": "meta_value"}

        # Call the function under test
        with self.assertLogs(level=logging.INFO) as log:
            scraping.scrape_webpages_to_db(keywords_list, mock_collection)

        # Assertions
        mock_search.assert_called_once_with("test combined keyword", num_results=3)
        mock_requests_get.assert_called()
        mock_contains_keywords.assert_called_with("Test content including test vocab. <br>", "test vocab")
        mock_collection.insert_one.assert_called()
        mock_meta_scraping.assert_called()

        # Verify log messages
        self.assertIn("Starting Google search for: 'test combined keyword'", log.output[0])
        self.assertIn("Page HTML stored in DB: http://example.com/test1.html", log.output[-1])

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.remove')  # Mock os.remove to avoid deleting real files
    @patch('functions.scraping.requests.get')
    @patch('functions.scraping.search')  # Replace 'functions.scraping' with your module's name
    @patch('functions.scraping.contains_keywords')
    @patch('functions.scraping.pdf_to_text')
    @patch('functions.scraping.pdf_meta_scraping')
    @patch('functions.scraping.meta_scraping')
    def test_scrape_webpages_to_db_pdf(self, mock_meta_scraping, mock_pdf_meta_scraping, mock_pdf_to_text, 
                                    mock_contains_keywords, mock_search, mock_requests_get, 
                                    mock_os_remove, mock_open):
        # Mock MongoDB collection
        mock_collection = MagicMock()

        # Ensure `find_one` always returns None, simulating a new URL
        mock_collection.find_one.side_effect = lambda query: None

        # Mock input data
        keywords_list = [
            ("test combined keyword", "test vocab", "test location")
        ]

        # Mock search results
        mock_search.return_value = ["http://example.com/test1.pdf"]

        # Mock requests.get
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_response.content = b"%PDF-1.4 Fake PDF Content"  # Simulating binary PDF content
        mock_requests_get.return_value = mock_response

        # Mock pdf_to_text and pdf_meta_scraping
        mock_pdf_to_text.return_value = "Extracted PDF text including test vocab."
        mock_pdf_meta_scraping.return_value = {"author": "Test Author", "title": "Test Title"}

        # Call the function under test
        with self.assertLogs(level=logging.INFO) as log:
            scraping.scrape_webpages_to_db(keywords_list, mock_collection)

        # Assertions
        mock_search.assert_called_once_with("test combined keyword", num_results=3)
        mock_requests_get.assert_called()
        mock_pdf_to_text.assert_called_once_with("temp_pdf_0.pdf")
        mock_pdf_meta_scraping.assert_called_once_with("temp_pdf_0.pdf")
        mock_collection.insert_one.assert_called_once_with({
            "url": "http://example.com/test1.pdf",
            "keyword of scraping": "test vocab",
            "localisation of scraping": "test location",
            "content": "Extracted PDF text including test vocab.",
            "meta_data": {
                "file_type": "pdf",
                "source_url": "http://example.com/test1.pdf",
                "author": "Test Author",
                "title": "Test Title"
            }
        })

        # Verify log messages
        self.assertIn("Starting Google search for: 'test combined keyword'", log.output[0])
        self.assertIn("PDF content stored in DB from http://example.com/test1.pdf.", log.output[-1])

if __name__ == '__main__':
    unittest.main()
