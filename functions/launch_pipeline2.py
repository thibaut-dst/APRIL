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
            processed_data = process.process_document(document)
            db.store_processed_data(document["_id"], processed_data, collection_name)
            logging.info(f'Processed and stored document #{index + 1} with ID: {document_id}')
        
        except Exception as e:
            logging.error(f'Error processing document #{index + 1} with ID: {document_id}: {e}')


if __name__ == "__main__":
    try:
        logging.info("Pipeline execution started.")
        collection = db.get_collection()
        iterate_documents(collection)
        logging.info("Text processing execution completed successfully.")
    except Exception as e:
        logging.critical(f"Critical error in the text processing execution: {e}")
