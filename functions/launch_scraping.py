import scraping
import db
import logging


# Configure logging
logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)


class Pipeline:
    def __init__(self):
        # Initialize variables
        self.database = 'April'
        self.collection_name = 'Documents'
        self.uri = "mongodb://mongo:27017"
        self.vocabulary_path = 'data/Vocabulaire_Expert_CSV.csv'
        self.collection = None
        self.keywords_list = None

    def initialize_db(self):
        try:
            # Attempt to connect to the database
            self.collection = db.get_collection(
                db_name=self.database,
                collection_name=self.collection_name,
                uri=self.uri
            )
            logging.info("Successfully connected to the database.")
        except Exception as e:
            # Log and halt execution on a database connection error
            logging.error(f"Database connection failed: {e}")
            raise SystemExit(f"Database connection failed: {e}")

    def load_keywords(self):
        try:
            # Load keywords from the CSV
            self.keywords_list = scraping.read_and_shuffle_csv(self.vocabulary_path)
            logging.info(f"Loaded keywords from {self.vocabulary_path}")
        except FileNotFoundError:
            logging.error(f"CSV file not found: {self.vocabulary_path}")
            raise SystemExit(f"CSV file not found: {self.vocabulary_path}")
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
            raise SystemExit(f"Error reading CSV file: {e}")

    def run_scraping(self):
        logging.info("Starting the scraping process...")
        try:
            scraping.scrape_webpages_to_db(self.keywords_list, self.collection)
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
            raise SystemExit(f"An error occurred during scraping: {e}")

    def run_pipeline(self):
        logging.info("Document collection - Pipeline initialization")
        self.initialize_db()
        self.load_keywords()
        self.run_scraping()
        logging.info("Pipeline finished.")


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run_pipeline()
