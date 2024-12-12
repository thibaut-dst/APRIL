import scraping as scrape
import db as db
import text_processing as process
import pandas as pd
import logging


logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

def iterate_documents(collection_name: str, vocabulary_path: str):
    """
    Iterate over all documents in a collection, process each one and store the enriched data back
    """

    # Define a query to select documents without the 'cleaned_text' field 
    query = { "cleaned_text": { "$exists": False } }

    # Iterate over the filtered documents
    for index, document in enumerate(collection_name.find(query)):
        document_id = str(document["_id"])  # Extract the document ID
        logging.info(f'Starting nlp for document ID: {document_id}')

        try:
            processed_data = process.process_document(document, vocabulary_path)
            db.store_processed_data(document["_id"], processed_data, collection_name)
        
        except Exception as e:
            logging.error(f'Error processing document ID: {document_id}: {e}')


if __name__ == "__main__":
    try:
        logging.info("Pipeline execution started.")
        collection = db.get_collection()
        vocabulary_path = 'Vocabulaire_Expert_CSV.csv'
        iterate_documents(collection, vocabulary_path)
        logging.info("Text processing execution completed successfully.")
    except Exception as e:
        logging.critical(f"Critical error in the text processing execution: {e}")
