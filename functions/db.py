from pymongo import MongoClient

db = 'April'
collection = 'Documents'
uri="mongodb://localhost:27017"

def get_collection(db_name = db, collection_name = collection, uri = uri):
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