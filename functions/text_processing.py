import re
from urllib.parse import urlparse
import db as db
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

file_path = 'Vocabulaire_Expert_CSV.csv'

def extract_columns_to_list(file_path):
    try:
        # Attempt to read the CSV file
        df = pd.read_csv(file_path, sep=";")
        
        # Extract the values from 'Vocabulaire de recherche' and 'Vocabulaire d'analyse' columns, excluding NaN values
        vocabulaire_recherche = df['Vocabulaire de recherche'].dropna().tolist()  # Exclude NaN in the first column
        vocabulaire_analyse = df["Vocabulaire d'analyse"].dropna().tolist()  # Exclude NaN in the third column

        
        # Combine both columns' values into one list
        combined_list = vocabulaire_recherche + vocabulaire_analyse
        print(len(vocabulaire_recherche), len(vocabulaire_analyse), len(combined_list))

        # Log the number of elements in the final list
        logging.info(f"Number of elements in the combined list: {len(combined_list)}")

        return combined_list
    except Exception as e:
        #print(f"An error occurred: {e}")
        logging.error(f"An error occurred: {e}")
        raise SystemExit(f"An error occurred: {e}")

target_words = extract_columns_to_list(file_path)

#print(target_words)


def get_domain_name(url: str) -> Optional[str]:
    """
    Extract the domain name from a URL.
    
    Parameters:
        url (str): The URL from which to extract the domain name.
        
    Returns:
        Optional[str]: The domain name if found; otherwise, None if extraction fails.
    """
    try:
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
        word_count = {word: 0 for word in target_words}
    
        # Tokenize the text and check for specific words
        for token in spacy_doc:
            if not token.is_punct:  # Exclude punctuation
                if token.lemma_.lower() in word_count:  # Check if the word is in our list
                    word_count[token.lemma_.lower()] += 1
        return word_count
    except Exception as e:
        logging.error(f"Error on word tracking: {e}")
        raise SystemExit(f"Error on word tracking: {e}")

def get_pdf_title_from_url(source_url):
    """
    Extract the file name from the source_url to use as the Title for PDF documents.

    Parameters:
        source_url (str): The URL of the PDF document.

    Returns:
        str: The extracted file name or None if the extraction fails.
    """
    try:
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


def process_document(MongoDB_document: dict) -> dict:
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
    
        if MongoDB_document["meta_data"]["file_type"] == "pdf" and "source_url" in MongoDB_document["meta_data"]:
            updated_title = get_pdf_title_from_url(MongoDB_document["meta_data"]["source_url"])
        else:
            updated_title = MongoDB_document["meta_data"].get("Title", None)

        data = {
            'Title_updated': updated_title,
            'domain': get_domain_name(MongoDB_document["url"]),
            'cleaned_text': cleaned_text,
            'named_entities': ner(spacy_document),
            'vocabulary_of_interest': word_tracking(spacy_document, target_words)
        }

        logging.info("Enriched data ready")
        return data
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise SystemExit(f"Error processing document: {e}")


""" if __name__ == "__main__":
    try:
        logging.info("Pipeline execution started.")
        collection = db.get_collection()
        iterate_documents(collection)
        logging.info("Text processing execution completed successfully.")
    except Exception as e:
        logging.critical(f"Critical error in the text processing execution: {e}")
 """