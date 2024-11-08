import functions.scraping as scrape
import functions.db as db
import functions.text_processing as process
import pandas as pd

def main():
    collection = db.get_collection()

    # Charger les mots-clés du CSV
    file_path = 'cleaned_keywords.csv'
    keywords_df = pd.read_csv(file_path)

    scrape.scrape_webpages_to_db(keywords_df, collection)

if __name__ == "__main__":
    main()