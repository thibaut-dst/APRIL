from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError
import logging

logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

database = 'April'
collection = 'Documents'
uri="mongodb://mongo:27017"

def get_collection(db_name = database, collection_name = collection, uri = uri):
    """
    Connects to a MongoDB instance and returns the specified collection.
    If the database or collection does not exist, MongoDB will create it on the first write operation.

    Parameters:
        db_name (str): The name of the database.
        collection_name (str): The name of the collection.
        uri (str): The MongoDB URI string. Default is 'mongodb://localhost:27017'.

    Returns:
        Collection: A MongoDB collection object.

    Raises:
        Exception: If the connection to MongoDB fails.
    """
    try:
        # Attempt to connect to MongoDB
        client = MongoClient(uri, serverSelectionTimeoutMS=20000)  # Timeout set to 20 seconds
        client.server_info()         # Force a connection to check the server's availability
        db = client[db_name]
        return db[collection_name]

    except (ConnectionFailure, ServerSelectionTimeoutError, ConfigurationError) as e:
        # Log and re-raise connection issues
        raise Exception(f"Failed to connect to MongoDB: {e}")


def store_processed_data(document_id: ObjectId, processed_data: dict, collection: Collection) -> None:
    """
    Update a MongoDB document with the processed data fields (cleaned text, ner, target word counts, etc.)
    
    Parameters:
        document_id (ObjectId): The unique identifier of the document to update.
        processed_data (dict): A dictionary of processed data to store in MongoDB.
                               Each key-value pair in the dictionary is added to the document.
        collection (Collection): The MongoDB collection in which the document resides.    
    """

    try:
        # Attempt to update the document
        result = collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": processed_data}
        )
        
        # Log the outcome of the update operation
        if result.matched_count == 0:
            logging.warning(f"Tried to update (post NLP) but document found with ID: {document_id}")
        else:
            print(f"Document with ID: {document_id} successfully updated.")
            logging.info(f"Successfully processed (NLP): {document_id}")

    except Exception as e:
        logging.error(f"Error updating (post NLP) document ID: {document_id}: {e}")
        raise
