import unittest
from unittest.mock import patch, MagicMock
import tempfile
import pandas as pd
import spacy
import os

from functions import text_processing

class TestProcessingFunctions(unittest.TestCase):
    def test_clean_text(self):
        test_cases = [
            ("This is  a test.\n\n\tText with newlines and tabs.", "This is a test. Text with newlines and tabs."),
            ("Multiple    spaces    in    text.", "Multiple spaces in text."),
            ("\n\nMultiple newlines at the start.", "Multiple newlines at the start."),
            ("Text with  multiple   spaces,   tabs\tand newlines.\t", "Text with multiple spaces, tabs and newlines."),
            ("SingleWord", "SingleWord"),  # Test with a simple word
            ("", ""),  # Test with empty string
            ("   ", "")  # Test with spaces only
        ]

        for text, expected in test_cases:
            with self.subTest(text=text):
                self.assertEqual(text_processing.clean_text(text), expected)

class TestNLPFunctions(unittest.TestCase):
    def test_valid_column(self):
        # Creates a temporary CSV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            file_path = temp_file.name
            data = {
                "Vocabulaire de recherche": ["mot1", "mot2", None, "mot4"],
                "Vocabulaire d'analyse": ["analyse1", None, "analyse3", "analyse4"]
            }
            df = pd.DataFrame(data)
            df.to_csv(file_path, sep=";", index=False)

        try:
            # Test pour une colonne valide
            result = text_processing.extract_columns_to_list(file_path, "Vocabulaire de recherche")
            expected = ["mot1", "mot2", "mot4"]  # Valeurs non NaN de la colonne
            self.assertEqual(result, expected)
        finally:
            # Supprime le fichier temporaire
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_top_5_words(self):
        # Input data sets
        words_of_research = {"data": 10, "analysis": 5, "python": 7, "code": 3, "machine": 6}
        words_of_analysis = {"data": 4, "science": 8, "python": 3, "learning": 5, "AI": 9}
        
        # Call the function
        result = text_processing.get_top_5_words(words_of_research, words_of_analysis)

        # Expected result (word combinations and sorting)
        expected = (['data', 'python', 'AI', 'science', 'machine'], [('data', 14), ('python', 10), ('AI', 9), ('science', 8), ('machine', 6)])
        
        self.assertEqual(result, expected)

    def test_relevance_score(self):
        # Load spaCy model
        nlp = spacy.load("en_core_web_sm")

        # Example of text
        text = "Data science and machine learning are transforming industries."

        # Process text with spaCy
        doc = nlp(text)

        # Dictionary of target words
        words_of_research_and_analysis = {"data": 10, "science": 5, "learning": 3, "AI": 2}

        # Call the function
        relevance_score = text_processing.calculate_relevance(doc, words_of_research_and_analysis)

        # Total occurrences of target words in the text
        # "data" (1), "science" (1), "learning" (1) => Total : 3
        # Total significant words (without empty words or punctuation): [‘data’, ‘science’, ‘machine’, ‘learning’, ‘transforming’, ‘industries’] => Total: 6
        # Relevance = 3 / 6 = 0.5
        expected_score = 0.5

        # Checking the expected score
        self.assertAlmostEqual(relevance_score, expected_score, places=2)

    def test_domain_extraction(self):
        test_cases = [
            ("https://www.example.com/path/to/resource", "www.example.com"),
            ("http://subdomain.example.com/resource", "subdomain.example.com"),
            ("https://example.com", "example.com"),
            ("www.example.com/path/to/resource", "www.example.com"),
            ("not-a-valid-url", "not-a-valid-url")
        ]

        for url, expected_domain in test_cases:
            with self.subTest(url=url):
                #print(text_processing.get_domain_name(url), expected_domain)
                self.assertEqual(text_processing.get_domain_name(url), expected_domain)

    def test_ner(self):
        # Load the spaCy model for French
        nlp = spacy.load("fr_core_news_lg")

        # Test cases: list of texts and expected results
        test_cases = [
            ("Apple is looking at buying U.K. startup for $1 billion", 
             {"ORG": ["Apple"]}),
            ("Barack Obama was born in Hawaii.", 
             {"PER": ["Barack Obama"], "LOC": ["Hawaii"]}),
            ("Google, headquartered in Mountain View, unveiled the new Android phone.", 
             {"ORG": ["Google"], "MISC": ["headquartered in Mountain View"]}),
            #("There is no named entity here.", 
            # {})
        ]

        # Test each case
        for text, expected_entities in test_cases:
            with self.subTest(text=text):
                # Process the text with spaCy
                doc = nlp(text)
                
                # Calls the ner function
                result = text_processing.ner(doc)  # Use the ner function directly


                # Compare expected results with those achieved
                self.assertEqual(result, expected_entities)

    def test_word_tracking(self):
        # Load the spaCy model for French
        nlp = spacy.load("fr_core_news_lg")

        # Test cases: list of texts and expected results
        test_cases = [
            ("Apple is looking at buying U.K. startup for $1 billion", 
             ["apple", "startup", "billion"], 
             {"apple": 1, "startup": 1, "billion": 1}),
            ("Barack Obama was born in Hawaii.", 
             ["barack", "hawaii", "president"], 
             {"barack": 1, "hawaii": 1, "president": 0}),
            ("Google, headquartered in Mountain View, unveiled the new Android phone.", 
             ["google", "android", "mountain", "view"], 
             {"google": 1, "android": 1, "mountain": 1, "view": 1}),
            ("Elon Musk announced a new project.", 
             ["elon", "musk", "project"], 
             {"elon": 1, "musk": 1, "project": 1}),
            ("This is a simple test to check the word tracking functionality.", 
             ["simple", "tracking", "functionality"], 
             {"simple": 1, "tracking": 1, "functionality": 1}),
            ("No target words here.", 
             ["word", "target"], 
             {"word": 1, "target": 1}),
            ("Le gouvernement vient de publier au journal officiel de la République la liste des 126 communes françaises "'prioritaires'" quant aux effets de l'érosion du littoral. En Occitanie, Collioure, Fleury-d'Aude et Villeneuve-lès-Maguelone sont les trois seules concernées pour l'instant. Le samedi 30 avril, la liste des 126 communes françaises dites "'prioritaires'" concernant les effets de l'érosion du littoral a été publiée au Journal Officiel de la République (sachant qu'à terme 864 communes sont potentiellement menacées par le recul du trait de côte). Trois sont situées en région Occitanie : Collioure dans les Pyrénées-Orientales, Fleury-d'Aude et Villeneuve-lès-Maguelone dans l'Hérault.", 
             ["trait de côte"],
             {"trait de côte": 1})
        ]

        # Test each case
        for text, targets, expected_word_count in test_cases:
            with self.subTest(text=text, targets=targets):
                # Traite le texte avec spaCy
                doc = nlp(text)
                
                # Calls the word_tracking function
                result = text_processing.word_tracking(doc, targets)

                # Compare expected results with those achieved
                self.assertEqual(result, expected_word_count)

    def test_get_pdf_title_from_url(self):
        # Fake URLs for different file types
        fake_urls = [
            # Fictitious PDF links
            "http://example.com/documentation/example1.pdf",
            "https://fakewebsite.org/resources/guide123.pdf",
            "http://mysite.fake/docs/manual_v2.pdf",

            # Dummy HTML links
            "http://example.com/home/index.html",
            "https://fakesite.net/blog/post.html",
            "http://nonexistentpage.xyz/pages/info.html",
            # Other fictitious formats
            "https://example-site.com/data/file.txt",
            "http://placeholder.org/files/sample.json",
            "https://my-fake-domain.fake/download/report.docx"
        ]

        # Expected results for PDF URLs
        expected_titles = [
            "example1.pdf",
            "guide123.pdf",
            "manual_v2.pdf",

            None,  # HTML: should return None or another meaningful value
            None,
            None,
            None,  # Other formats: None or another significant value
            None,
            None
        ]

        for url, expected_title in zip(fake_urls, expected_titles):
            with self.subTest(url=url):
                result = text_processing.get_pdf_title_from_url(url)
                self.assertEqual(result, expected_title, f"Failed for URL: {url}")

    def test_process_document(self):
        """
        Je ne sais pas s'il en faut un ?
        """
        pass

if __name__ == '__main__':
    unittest.main()