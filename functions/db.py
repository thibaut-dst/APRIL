from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId

database = 'April'
collection = 'Documents'
uri="mongodb://localhost:27017"

def get_collection(db_name = database, collection_name = collection, uri = uri):
    """
    Connects to a MongoDB instance and returns the specified collection.
    If the database or collection does not exist, MongoDB will create it on the first write operation.

    Parameters:
        db_name (str): The name of the database.
        collection_name (str): The name of the collection.
        uri (str): The MongoDB URI string. Default is 'mongodb://localhost:27017'.

    Returns:
        collection: A MongoDB collection object.
    """
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection

def store_processed_data(document_id: ObjectId, processed_data: dict, collection: Collection) -> None:
    """
    Update a MongoDB document with the processed data fields (cleaned text, ner, target word counts, etc.)
    
    Parameters:
        document_id (ObjectId): The unique identifier of the document to update.
        processed_data (dict): A dictionary of processed data to store in MongoDB.
                               Each key-value pair in the dictionary is added to the document.
        collection (Collection): The MongoDB collection in which the document resides.    
    """

    collection.update_one(
        {"_id": document_id},
        {"$set": processed_data}
    )