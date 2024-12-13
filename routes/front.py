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