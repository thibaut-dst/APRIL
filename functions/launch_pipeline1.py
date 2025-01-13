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


def main():
    logging.info("Document collection - Pipeline initialization")
    
    database = 'April'
    collection_name = 'Documents'
    uri="mongodb://mongo:27017"
    vocabulary_path = 'data/Vocabulaire_Expert_CSV.csv'

    try:
        # Attempt to connect to the database
        collection = db.get_collection(db_name=database, collection_name=collection_name, uri= uri)
        logging.info("Successfully connected to the database.")
    except Exception as e:
        # Log and halt execution on a database connection error
        logging.error(f"Database connection failed: {e}")
        raise SystemExit(f"Database connection failed: {e}")

    # Load keywords from the CSV
    try:
        keywords_list = scraping.read_and_shuffle_csv(vocabulary_path)
        logging.info(f"Loaded keywords")
    except FileNotFoundError:
        logging.error(f"CSV file not found: {vocabulary_path}")
        raise SystemExit(f"CSV file not found: {vocabulary_path}")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        raise SystemExit(f"Error reading CSV file: {e}")

    

    logging.info("Starting the scraping process...")
    try:
        scraping.scrape_webpages_to_db(keywords_list, collection)
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
        raise SystemExit(f"An error occurred during scraping: {e}")

    logging.info("Pipeline finished.")
    
if __name__ == "__main__":
    main()

