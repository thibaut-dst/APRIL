import re
from urllib.parse import urlparse
#import db as db
import pandas as pd
import spacy
from typing import Optional
from spacy.tokens import Doc
nlp = spacy.load("fr_core_news_lg")
import logging


logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
) 


def extract_columns_to_list(file_path: str, column_name: str) -> list:
    try:
        # Attempt to read the CSV file
        df = pd.read_csv(file_path, sep=";")
        """
        # Extract the values from 'Vocabulaire de recherche' and 'Vocabulaire d'analyse' columns, excluding NaN values
        #vocabulaire_recherche = df['Vocabulaire de recherche'].dropna().tolist()  # Exclude NaN in the first column
        #vocabulaire_analyse = df["Vocabulaire d'analyse"].dropna().tolist()  # Exclude NaN in the third column
        """
        if column_name not in df.columns:
            logging.error(f"Column '{column_name}' does not exist in the CSV file.")
            raise SystemExit(f"Column '{column_name}' does not exist in the CSV file.")
        else :
            # Extract the values from column_name excluding NaN values
            vocabulaire = df[column_name].dropna().tolist()
            """
            # Combine both columns' values into one list
            combined_list = vocabulaire_recherche + vocabulaire_analyse
            print(len(vocabulaire_recherche), len(vocabulaire_analyse), len(combined_list))
            """
            # Log the number of elements in the final list
            #logging.info(f"Number of elements in the combined list: {len(vocabulaire)}")

            return vocabulaire
    except FileNotFoundError:
        logging.error(f"The file {file_path} was not found.")
        raise SystemExit(f"The file {file_path} was not found.")
    except pd.errors.ParserError:
        logging.error(f"Error parsing CSV file {file_path}. Check the file format.")
        raise SystemExit(f"Error parsing CSV file {file_path}.")
    except KeyError as e:
        logging.error(f"Column {e} not found in the CSV file.")
        raise SystemExit(f"Column {e} not found in the CSV file.")


def get_top_5_words(words_of_research: dict, words_of_analysis: dict) -> list:
    """
    Combine the word counts from 'words_of_research' and 'words_of_analysis', then extract the top 5 most frequent words.

    Parameters:
        words_of_research (dict): Dictionary with word counts from research-related words.
        words_of_analysis (dict): Dictionary with word counts from analysis-related words.

    Returns:
        list: List of the top 5 words sorted by their occurrence count in descending order.
    """
    try:
        # Combine both dictionaries by summing counts for common words
        combined_word_count = words_of_research.copy()  # Start with words_of_research
        for word, count in words_of_analysis.items():
            if word in combined_word_count:
                combined_word_count[word] += count
            else:
                combined_word_count[word] = count

        # Sort the combined dictionary by count in descending order
        sorted_words = sorted(combined_word_count.items(), key=lambda item: item[1], reverse=True)

        # Extract the top 5 most frequent words
        top_5_words = [word for word, count in sorted_words[:5]]
        # Extract the top 5 most frequent words along with their counts
        top_5_words_count = [(word, count) for word, count in sorted_words[:5]]

        return top_5_words, top_5_words_count
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise SystemExit(f"An error occurred: {e}")


def calculate_relevance(spacy_doc: Doc, words_of_research_and_analysis: dict) -> float:
    """
    Calculate the relevance of a text based on the occurrence of words from 'words_of_research_and_analysis'.
    The relevance is calculated as the proportion of target word occurrences relative to the total number of words in the text.

    Parameters:
        spacy_doc (Doc): A spaCy Doc object with the processed text.
        words_of_research_and_analysis (dict): Dictionary with word counts from both research-related and analysis-related words.

    Returns:
        float: A relevance score normalized between 0 and 1 based on the relative frequency of target word occurrences.
    """
    try:
        # Filter out stop words and punctuation from the text
        content_words = [token.text.lower() for token in spacy_doc if not token.is_punct and not token.is_stop]

        # Create a dictionary of word frequencies for the text
        word_frequencies = {}
        for word in content_words:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1

        # Calculate the overlap of words between the text and the target dictionary
        target_word_occurrences = sum(word_frequencies.get(word, 0) for word in words_of_research_and_analysis.keys())

        if target_word_occurrences == 0:
            logging.warning("No target words found in the document.")
            return 0.0

        # Total number of content words (excluding stop words and punctuation)
        total_content_words = len(content_words)

        # Calculate and normalize the relevance score
        relevance_score = target_word_occurrences / total_content_words if total_content_words > 0 else 0.0

        return relevance_score, total_content_words
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise SystemExit(f"An error occurred: {e}")  


def get_domain_name(url: str) -> Optional[str]:
    """
    Extract the domain name from a URL.
    
    Parameters:
        url (str): The URL from which to extract the domain name.
        
    Returns:
        Optional[str]: The domain name if found; otherwise, None if extraction fails.
    """
    try:
        # If the URL doesn't contain 'http://' or 'https://', prepend 'http://'
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
            
        pattern = r'https?://([^/]+)'
        match = re.search(pattern, url)
        if match:
            domain = match.group(1)
            logging.info(f"Domain name: {domain} for {url}")
            return domain
        else:
            #print(f"Error on domain name extraction for {url}")
            #logging.info(f"Error on domain name extraction for {url}")
            return url
    except Exception as e:
        logging.error(f"Error on domain name extraction: {e}")
        raise SystemExit(f"Error on domain name extraction: {e}")        


def clean_text(text: str) -> str:
    """
    Cleans up sequences of unwanted whitespace characters, such as multiple newlines, tabs,
    and excessive spaces, replacing them with a single space.
    
    Parameters:
        text (str): The raw text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    try:
        if not isinstance(text, str):
            logging.error("Input text is not a string.")
            raise ValueError("Input text is not a string.")
        else :
            text = re.sub(r'[\n\t\r]+', ' ', text) # Replace sequences of newline, tab, or carriage return characters with a single space
            text = re.sub(r'\s{2,}', ' ', text).strip() # Replace multiple spaces with a single space
            return text
    except Exception as e:
        logging.error(f"Error on text cleaning: {e}")
        raise SystemExit(f"Error on text cleaning: {e}")


def ner(spacy_doc: Doc) -> dict:
    """
    Perform named entity recognition on a given spaCy Doc object, ensuring no duplicate entity texts.
    
    Parameters:
        spacy_doc (Doc): A spaCy Doc object with processed text.

    Returns:
        dict: A dictionary with entity labels as keys and lists of unique entity texts as values.
    """
    try:
        if not isinstance(spacy_doc, Doc):
            logging.error("Input is not a valid spaCy Doc object.")
            raise ValueError("Input is not a valid spaCy Doc object.")
        if not spacy_doc.ents:
            logging.warning("No named entities found in the document.")
        entities = {}

        for ent in spacy_doc.ents:
            if ent.label_ not in entities:
                entities[f'{ent.label_}'] = set()  # Use a set to avoid duplicates
            entities[f'{ent.label_}'].add(ent.text)  # Add entity text to the set
        
        # Convert sets to lists for the final output
        entities = {label: list(texts) for label, texts in entities.items()}
        
        return entities
    except Exception as e:
        logging.error(f"Error on named entity recognition: {e}")
        raise SystemExit(f"Error on named entity recognition: {e}")


def word_tracking(spacy_doc: Doc, targets: list[str]) -> dict:
    """
    Track and count occurrences of specific target words within a spaCy Doc object.
    
    Parameters:
        targets (list[str]): List of target words to track in the text.
        spacy_doc (Doc): A spaCy Doc object with processed text.
        
    Returns:
        dict: Dictionary with target words as keys and their respective occurrence counts as values.
    """
    try:
        if not isinstance(spacy_doc, Doc):
            logging.error("Input is not a valid spaCy Doc object.")
            raise ValueError("Input is not a valid spaCy Doc object.")

        word_count = {word: 0 for word in targets}
    
        # Tokenize the text and check for specific words
        for token in spacy_doc:
            if not token.is_punct:  # Exclude punctuation
                if token.lemma_.lower() in word_count:  # Check if the word is in our list
                    word_count[token.lemma_.lower()] += 1
        return word_count
    except Exception as e:
        logging.error(f"Error on word tracking: {e}")
        raise SystemExit(f"Error on word tracking: {e}")


def get_pdf_title_from_url(source_url: str) -> str:
    """
    Extract the file name from the source_url to use as the Title for PDF documents.

    Parameters:
        source_url (str): The URL of the PDF document.

    Returns:
        str: The extracted file name or None if the extraction fails.
    """
    try:
        if not source_url or not source_url.startswith("http"):
            logging.error(f"Invalid or missing URL: {source_url}")
            raise ValueError(f"Invalid or missing URL: {source_url}")
        # Parse the URL and extract the path
        parsed_url = urlparse(source_url)
        file_name = parsed_url.path.split("/")[-1]  # Get the last part of the URL path

        # Ensure it's a valid PDF file name
        if file_name.lower().endswith(".pdf"):
            return file_name

        logging.warning(f"URL does not contain a valid PDF file name: {source_url}")
        return None
    except Exception as e:
        logging.error(f"Error extracting PDF title from URL ({source_url}): {e}")
        return None


def process_document(MongoDB_document: dict, vocabulary_path: str) -> dict:
    """
    Centralization of the processing logic:
    Processes a single document to extract the cleaned text, domain name, named entities,
    and counts of target words.
    
    Parameters:
        document (dict): A dictionary representing a single MongoDB document.
        
    Returns:
        dict: A dictionary containing the processed data with keys for 'cleaned_text',
              'domain', 'named_entities', and 'vocabular_of_interest'.
    """
    try:
        raw_text = MongoDB_document["content"]
        cleaned_text = clean_text(raw_text)
        spacy_document = nlp(cleaned_text)
        target_words_research = extract_columns_to_list(vocabulary_path, 'Vocabulaire de recherche')
        target_words_analysis = extract_columns_to_list(vocabulary_path, "Vocabulaire d'analyse")
        words_of_research = word_tracking(spacy_document, target_words_research)
        words_of_analysis = word_tracking(spacy_document, target_words_analysis)
        top_5_words, top_5_words_count = get_top_5_words(words_of_research, words_of_analysis)
        relevance_score, total_content_words = calculate_relevance(spacy_document,{ **words_of_research, **words_of_analysis})


        if MongoDB_document["meta_data"]["file_type"] == "pdf" and "source_url" in MongoDB_document["meta_data"]:
            updated_title = get_pdf_title_from_url(MongoDB_document["meta_data"]["source_url"])
        else:
            updated_title = MongoDB_document["meta_data"].get("Title", None)

        data = {
            'tagged': 0,
            'Title_updated': updated_title,
            'domain': get_domain_name(MongoDB_document["url"]),
            'cleaned_text': cleaned_text,
            'named_entities': ner(spacy_document),
            'vocabulary_of_interest': {
                'words_of_research' : words_of_research,
                'words_of_analysis' : words_of_analysis,
                'Top_5_words' : top_5_words_count,
                'Pertinence' : relevance_score,
                'Document_Token_Weight' : total_content_words
                }
        }

        return data
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise SystemExit(f"Error processing document: {e}")

