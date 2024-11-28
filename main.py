import functions.scraping as scrape
import functions.db as db
import functions.text_processing as process
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

def main():
    logging.info("Pipeline initialization.")

    try:
        # Attempt to connect to the database
        collection = db.get_collection()
        logging.info("Successfully connected to the database.")
    except Exception as e:
        # Log and halt execution on a database connection error
        logging.error(f"Database connection failed: {e}")
        raise SystemExit(f"Database connection failed: {e}")

    # Load keywords from the CSV
    file_path = 'cleaned_keywords.csv'
    try:
        keywords_df = pd.read_csv(file_path)
        logging.info(f"Loaded keywords")
    except FileNotFoundError:
        logging.error(f"CSV file not found: {file_path}")
        raise SystemExit(f"CSV file not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        raise SystemExit(f"Error reading CSV file: {e}")

    

    logging.info("Starting the scraping process...")
    try:
        scrape.scrape_webpages_to_db(keywords_df, collection)
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
        raise SystemExit(f"An error occurred during scraping: {e}")

    logging.info("Pipeline finished.")
if __name__ == "__main__":
    main()

