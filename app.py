from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)


app.config["MONGO_URI"] = "mongodb://localhost:27017/April"
mongo = PyMongo(app)
mongo_collection = mongo.db.Documents


@app.route('/')

def index():
    documents = mongo_collection.find()
    return render_template('index.html', documents=documents)

# Route to view a single document by ID
@app.route('/document/<doc_id>')
def document(doc_id):
    document = mongo_collection.find_one({'_id': ObjectId(doc_id)})
    return render_template('document.html', document=document)

if __name__ == '__main__':
    app.run(debug=True)
