from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # replace with your MongoDB URI
db = client['April']  # replace with your database name
collection = db['Documents']  # replace with your collection name

# Helper function to convert MongoDB document to JSON
def document_to_json(doc):
    return {
        "_id": str(doc["_id"]),
        "url": doc.get("url"),
        "keyword": doc.get("keyword"),
        "content": doc.get("content"),
        "meta_data": doc.get("meta_data")
    }

# Route to retrieve all documents
@app.route('/documents', methods=['GET'])
def get_all_documents():
    docs = collection.find()
    result = [document_to_json(doc) for doc in docs]
    return jsonify(result), 200

# Route to retrieve a document by its ObjectId
@app.route('/documents/<string:id>', methods=['GET'])
def get_document_by_id(id):
    try:
        doc = collection.find_one({"_id": ObjectId(id)})
        if doc:
            return jsonify(document_to_json(doc)), 200
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to retrieve documents based on keyword
@app.route('/documents/keyword', methods=['GET'])
def get_documents_by_keyword():
    keyword = request.args.get('keyword')
    docs = collection.find({"keyword": keyword})
    result = [document_to_json(doc) for doc in docs]
    return jsonify(result), 200

# Route to retrieve documents based on URL
@app.route('/documents/url', methods=['GET'])
def get_documents_by_url():
    url = request.args.get('url')
    doc = collection.find_one({"url": url})
    if doc:
        return jsonify(document_to_json(doc)), 200
    else:
        return jsonify({"error": "Document not found"}), 404

# Route to retrieve documents based on metadata fields
@app.route('/documents/metadata', methods=['GET'])
def get_documents_by_metadata():
    title = request.args.get('title')
    description = request.args.get('description')
    query = {}
    
    if title:
        query["meta_data.Title"] = title
    if description:
        query["meta_data.Description"] = description
    
    docs = collection.find(query)
    result = [document_to_json(doc) for doc in docs]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
