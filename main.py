import functions.scraping as scrape
import functions.db as db
import functions.text_processing as process
import functions.nlp as NLP
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
    logging.info("Pipeline started.")
    collection = db.get_collection()

    # Charger les mots-clés du CSV
    file_path = 'cleaned_keywords.csv'
    keywords_df = pd.read_csv(file_path)
    
    logging.info("Starting the scraping process...")
    scrape.scrape_webpages_to_db(keywords_df, collection)

    logging.info("Pipeline finished.")

if __name__ == "__main__":
    main()

