from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Blueprint, current_app, render_template

api_mongo = Blueprint('api_mongo', __name__)


@api_mongo.route('/get-doc-count', methods=['GET'])
def get_doc_count():
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents
    count = mongo_collection.count_documents({})
    return jsonify({'count': count})

@api_mongo.route('/get-doc-processed-count', methods=['GET'])
def get_doc_processed_count():
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents
    query = {"cleaned_text": {"$exists": True}} 
    count = mongo_collection.count_documents(query) 
    return jsonify({'count': count})
