import db
import text_processing
import logging


# Configure logging
logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)


class TextProcessingPipeline:
    def __init__(self):
        # Initialize variables
        self.database = 'April'
        self.collection_name = 'Documents'
        self.uri = "mongodb://mongo:27017"
        self.vocabulary_path = 'data/Vocabulaire_Expert_CSV.csv'
        self.collection = None

    def initialize_db(self):
        try:
            # Connect to the database and get the collection
            self.collection = db.get_collection(
                db_name=self.database,
                collection_name=self.collection_name,
                uri=self.uri
            )
            logging.info("Successfully connected to the database.")
        except Exception as e:
            logging.critical(f"Database connection failed: {e}")
            raise SystemExit(f"Database connection failed: {e}")

    def iterate_documents(self):
        """
        Iterate over all documents in a collection, process each one, and store the enriched data back.
        """
        # Query to select documents without the 'cleaned_text' field
        query = {"cleaned_text": {"$exists": False}}

        for index, document in enumerate(self.collection.find(query)):
            document_id = str(document["_id"])  # Extract the document ID
            logging.info(f"Starting NLP for document ID: {document_id}")

            try:
                # Process document and store the enriched data
                processed_data = text_processing.process_document(document, self.vocabulary_path)
                db.store_processed_data(document["_id"], processed_data, self.collection)
            except Exception as e:
                logging.error(f"Error processing document ID: {document_id}: {e}")

    def run_pipeline(self):
        logging.info("Document processing (NLP) - Pipeline initialization")
        self.initialize_db()
        self.iterate_documents()
        logging.info("Text processing execution completed successfully.")


if __name__ == "__main__":
    pipeline = TextProcessingPipeline()
    pipeline.run_pipeline()
