from pymongo import MongoClient
import functions.db as db



if __name__ == "__main__":
    collection = db.get_collection()

    # Retrieve documents and print their _id values
    for document in collection.find():
        # Get the _id and convert it to a string
        document_id = str(document["_id"])
        print(document_id)
