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
        # Crée un fichier CSV temporaire
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
        # Jeux de données d'entrée
        words_of_research = {"data": 10, "analysis": 5, "python": 7, "code": 3, "machine": 6}
        words_of_analysis = {"data": 4, "science": 8, "python": 3, "learning": 5, "AI": 9}
        
        # Appeler la fonction
        result = text_processing.get_top_5_words(words_of_research, words_of_analysis)

        # Résultat attendu (combinaisons et tri des mots)
        expected = (['data', 'python', 'AI', 'science', 'machine'], [('data', 14), ('python', 10), ('AI', 9), ('science', 8), ('machine', 6)])
        
        self.assertEqual(result, expected)

    def test_relevance_score(self):
        # Charger le modèle spaCy
        nlp = spacy.load("en_core_web_sm")

        # Exemple de texte
        text = "Data science and machine learning are transforming industries."

        # Traiter le texte avec spaCy
        doc = nlp(text)

        # Dictionnaire de mots cibles
        words_of_research_and_analysis = {"data": 10, "science": 5, "learning": 3, "AI": 2}

        # Appeler la fonction
        relevance_score = text_processing.calculate_relevance(doc, words_of_research_and_analysis)

        # Total des occurrences des mots cibles dans le texte
        # "data" (1), "science" (1), "learning" (1) => Total : 3
        # Total de mots significatifs (sans mots vides ni ponctuation) : ["data", "science", "machine", "learning", "transforming", "industries"] => Total : 6
        # Relevance = 3 / 6 = 0.5
        expected_score = 0.5

        # Vérification du score attendu
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
        # Charger le modèle spaCy pour le français
        nlp = spacy.load("fr_core_news_lg")

        # Cas de test : liste des textes et des résultats attendus
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

        # Teste chaque cas
        for text, expected_entities in test_cases:
            with self.subTest(text=text):
                # Traite le texte avec spaCy
                doc = nlp(text)
                
                # Appelle la fonction ner
                result = text_processing.ner(doc)  # Utilisez directement la fonction ner

                # Compare les résultats attendus avec ceux obtenus
                self.assertEqual(result, expected_entities)

    def test_word_tracking(self):
        # Charger le modèle spaCy pour le français
        nlp = spacy.load("fr_core_news_lg")

        # Cas de test : liste des textes et des résultats attendus
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
             {"word": 0, "target": 1})
        ]

        # Teste chaque cas
        for text, targets, expected_word_count in test_cases:
            with self.subTest(text=text, targets=targets):
                # Traite le texte avec spaCy
                doc = nlp(text)
                
                # Appelle la fonction word_tracking
                result = text_processing.word_tracking(doc, targets)

                # Compare les résultats attendus avec ceux obtenus
                self.assertEqual(result, expected_word_count)

    def test_get_pdf_title_from_url(self):
        # Faux URLs pour différents types de fichiers
        fake_urls = [
            # Liens PDF fictifs
            "http://example.com/documentation/example1.pdf",
            "https://fakewebsite.org/resources/guide123.pdf",
            "http://mysite.fake/docs/manual_v2.pdf",

            # Liens HTML fictifs
            "http://example.com/home/index.html",
            "https://fakesite.net/blog/post.html",
            "http://nonexistentpage.xyz/pages/info.html",
            # Autres formats fictifs
            "https://example-site.com/data/file.txt",
            "http://placeholder.org/files/sample.json",
            "https://my-fake-domain.fake/download/report.docx"
        ]

        # Résultats attendus pour les URLs PDF
        expected_titles = [
            "example1.pdf",
            "guide123.pdf",
            "manual_v2.pdf",

            None,  # HTML: devrait retourner None ou une autre valeur significative
            None,
            None,
            None,  # Autres formats : None ou une autre valeur significative
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