import functions.scraping as scrape
import functions.db as db
import functions.text_processing as process
import functions.nlp as NLP
import pandas as pd

def main():
    collection = db.get_collection()
    process.iterate_documents(collection)


if __name__ == "__main__":
    main()