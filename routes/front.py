from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Blueprint, current_app, render_template

front = Blueprint('front', __name__)


@front.route('/')
def index():
    # Access the database connection from the main app
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents
    documents = mongo_collection.find()
    return render_template('index.html', documents=documents)

@front.route('/launch-pipeline')
def launch_pipeline():
    return render_template('launch_pipeline.html')


@front.route('/document/<doc_id>')
def document(doc_id):
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents
    document = mongo_collection.find_one({'_id': ObjectId(doc_id)})
    if not document.get('cleaned_text'):
        return render_template('not_processed.html', document=document)
    return render_template('document.html', document=document)

@front.route('/documents')
def documents():
    # Get sorting parameters from query string
    sort_by = request.args.get('sort_by', 'title')  # Default to sorting by 'title'
    order = request.args.get('order', 'asc')       # Default to ascending order

    # Determine sorting direction
    sort_direction = 1 if order == 'asc' else -1

    # Access the MongoDB collection
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents

    # Fetch and sort documents from the database
    documents = mongo_collection.find().sort([(sort_by, sort_direction)])

    # Render the table with sorted documents
    return render_template('table.html', documents=documents, sort_by=sort_by, order=order)


@front.route('/update-tagged', methods=['POST'])
def update_tagged():
    try:
        data = request.get_json()
        doc_id = data.get('doc_id')
        value = data.get('value')

        if not doc_id or value not in [0, 1, 2]:  # Validate input
            return jsonify({"error": "Invalid data provided."}), 400

        mongo = current_app.mongo
        mongo_collection = mongo.db.Documents
        mongo_collection.update_one({'_id': ObjectId(doc_id)}, {'$set': {'tagged': value}})
        return jsonify({"message": f"Document {doc_id} tagged set to {value}."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500