import scraping as scrape
import db as db
import text_processing as process
import pandas as pd
import logging
import itertools
import random

# Configure logging
logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

def read_and_shuffle_csv(file_path):
    try:
        # Attempt to read the CSV file
        df = pd.read_csv(file_path, sep=";")

        # Extract the first two columns into lists
        vocabulaire_recherche = df['Vocabulaire de recherche'].dropna().tolist()  # First column
        localisation_recherche = df['Localisation de recherche'].dropna().tolist()  # Second column

        # Generate triples: [vocabulaire + localisation, vocabulaire, localisation]
        triple_list = [[f"{vocab} {loc.strip()}", vocab, loc.strip()] for vocab, loc in itertools.product(vocabulaire_recherche, localisation_recherche)]

        # Shuffle the triples randomly
        random.shuffle(triple_list)

        logging.info(f"Number of triples generated: {len(triple_list)}")
        return triple_list

    except Exception as e:
        print(f"An error occurred: {e}")

      

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
    file_path = 'Vocabulaire_Expert_CSV.csv'

    try:
        keywords_list = read_and_shuffle_csv(file_path)
        logging.info(f"Loaded keywords")
    except FileNotFoundError:
        logging.error(f"CSV file not found: {file_path}")
        raise SystemExit(f"CSV file not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        raise SystemExit(f"Error reading CSV file: {e}")

    

    logging.info("Starting the scraping process...")
    try:
        scrape.scrape_webpages_to_db(keywords_list, collection)
    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
        raise SystemExit(f"An error occurred during scraping: {e}")

    logging.info("Pipeline finished.")
    
if __name__ == "__main__":
    main()

