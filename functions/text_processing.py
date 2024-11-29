import re
import db as db
import spacy
from typing import Optional
from spacy.tokens import Doc
nlp = spacy.load("fr_core_news_lg")
from bson import ObjectId
import logging

logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

target_words_og = ['écologique', 'Océan', 'Occitanie']
target_words = [element.lower() for element in target_words_og]


def get_domain_name(url: str) -> Optional[str]:
    """
    Extract the domain name from a URL.
    
    Parameters:
        url (str): The URL from which to extract the domain name.
        
    Returns:
        Optional[str]: The domain name if found; otherwise, None if extraction fails.
    """
    pattern = r'https?://([^/]+)'
    match = re.search(pattern, url)
    if match:
        domain = match.group(1)
        return domain
    else:
        print(f"Error on domain name extraction for {url}")
        return url
    
def clean_text(text: str) -> str:
    """
    Cleans up sequences of unwanted whitespace characters, such as multiple newlines, tabs,
    and excessive spaces, replacing them with a single space.
    
    Parameters:
        text (str): The raw text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    text = re.sub(r'[\n\t\r]+', ' ', text) # Replace sequences of newline, tab, or carriage return characters with a single space
    text = re.sub(r'\s{2,}', ' ', text).strip() # Replace multiple spaces with a single space
    return text

def ner(spacy_doc: Doc) -> dict:
    """
    Perform named entity recognition on a given spaCy Doc object.
    
    Parameters:
        spacy_doc (Doc): A spaCy Doc object with processed text.

    Returns:
        dict: A dictionary with entity labels as keys and lists of entity texts as values.
    """
    entities = {}

    for ent in spacy_doc.ents:  
        if ent.label_ not in entities:
            entities[f'{ent.label_}'] = []
        entities[f'{ent.label_}'].append(ent.text)
    return entities

def word_tracking(spacy_doc: Doc, targets: list[str]) -> dict:
    """
    Track and count occurrences of specific target words within a spaCy Doc object.
    
    Parameters:
        targets (list[str]): List of target words to track in the text.
        spacy_doc (Doc): A spaCy Doc object with processed text.
        
    Returns:
        dict: Dictionary with target words as keys and their respective occurrence counts as values.
    """
    word_count = {word: 0 for word in target_words}
   
    # Tokenize the text and check for specific words
    for token in spacy_doc:
        if not token.is_punct:  # Exclude punctuation
            if token.lemma_.lower() in word_count:  # Check if the word is in our list
                word_count[token.lemma_.lower()] += 1
    return word_count

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
    raw_text = MongoDB_document["content"]
    cleaned_text = clean_text(raw_text)
    spacy_document = nlp(cleaned_text)

    data = {
        'domain': get_domain_name(MongoDB_document["url"]),
        'cleaned_text': cleaned_text,
        'named_entities': ner(spacy_document),
        'vocabulary_of_interest': word_tracking(spacy_document, target_words)
    }
    print("enriched data ready")
    return data

def iterate_documents(collection_name):
    """
    Iterate over all documents in a collection, process each one and store the enriched data back
    """

    # Define a query to select documents without the 'cleaned_text' field 
    query = { "cleaned_text": { "$exists": False } }
    # Iterate over the filtered documents
    for index, document in enumerate(collection_name.find(query)):
        document_id = str(document["_id"])  # Extract the document ID

        logging.info(f'Processing document #{index + 1} with ID: {document_id}')
        try:
            processed_data = process_document(document)
            db.store_processed_data(document["_id"], processed_data, collection_name)
            logging.info(f'Processed and stored document #{index + 1} with ID: {document_id}')
        
        except Exception as e:
            logging.error(f'Error processing document #{index + 1} with ID: {document_id}: {e}')

if __name__ == "__main__":
    try:
        logging.info("Pipeline execution started.")
        print("Pipeline execution started.")
        collection = db.get_collection()
        iterate_documents(collection)
        logging.info("Text processing execution completed successfully.")
        print("Text processing execution completed successfully.")
    except Exception as e:
        logging.critical(f"Critical error in the text processing execution: {e}")
        print(f"Critical error in the text processing execution: {e}")