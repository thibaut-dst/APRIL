import re
import db

# Function to process each document (you can define specific processing here)
def process_document(document):
    """
    Centralize text processing logic here
    """
    raw_text = document["content"]
    cleaned_text = clean_text(raw_text)
    print(cleaned_text, "\n\n")


def clean_text(text):
    """
    Cleans up sequences of unwanted whitespace characters, such as multiple newlines, tabs,
    and excessive spaces, replacing them with a single space.
    
    Parameters:
        text (str): The raw text to be cleaned.
        
    Returns:
        str: The cleaned text.
    """
    text = re.sub(r'[\n\t\r]+', ' ', text) # Replace sequences of newline, tab, or carriage return characters with a single space
    text = re.sub(r'\s{2,}', ' ', text).strip() # Replace multiple spaces with a single space
    return text

def iterate_documents(collection_name):
    """
    Iterate over all documents in a collection and process each one.
    """
    for document in collection_name.find():
        process_document(document)

if __name__ == "__main__":
    collection = db.get_collection("April", "Documents")

    iterate_documents(collection)