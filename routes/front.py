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