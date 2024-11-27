from flask import Flask, jsonify, request, render_template, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import threading
import os
import subprocess

app = Flask(__name__)

#===================== Database config =====================
app.config["MONGO_URI"] = "mongodb://localhost:27017/April"
mongo = PyMongo(app)
mongo_collection = mongo.db.Documents

#===================== Pipeline config =====================
pipeline_process = None

def log_pipeline_output(process):
    with open('pipeline.log', 'a') as log_file:
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                log_file.write(line)
                log_file.flush()

                error_line = process.stderr.readline()
                if not error_line:
                    break
                log_file.write(f"ERROR: {error_line}")
                log_file.flush()
        except Exception as e:
            log_file.write(f"Exception occurred in log_pipeline_output: {e}\n")
            log_file.flush()

@app.route('/start-pipeline', methods=['POST'])
def start_pipeline():
    global pipeline_process
    if pipeline_process and pipeline_process.poll() is None:
        return "Pipeline is already running.", 400

    try:
        pipeline_process = subprocess.Popen(
            ['python3', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )
        threading.Thread(target=log_pipeline_output, args=(pipeline_process,), daemon=True).start()
        return "Pipeline started."
    except Exception as e:
        with open('pipeline.log', 'a') as log_file:
            log_file.write(f"Failed to start pipeline: {str(e)}\n")
        return f"Failed to start pipeline: {str(e)}", 500

@app.route('/stop-pipeline', methods=['POST'])
def stop_pipeline():
    global pipeline_process
    if not pipeline_process or pipeline_process.poll() is not None:
        return "Pipeline is not running.", 400

    pipeline_process.terminate()
    pipeline_process = None
    return "Pipeline stopped."

@app.route('/get-logs', methods=['GET'])
def get_logs():
    log_file = 'pipeline.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()
        return jsonify({'logs': logs[-20:]})
    else:
        return jsonify({'logs': []})

@app.route('/get-doc-count', methods=['GET'])
def get_doc_count():
    count = mongo_collection.count_documents({})
    return jsonify({'count': count})

#===================== Document API =====================
def document_to_json(doc):
    return {
        "_id": str(doc["_id"]),
        "url": doc.get("url"),
        "keyword": doc.get("keyword"),
        "content": doc.get("content"),
        "meta_data": doc.get("meta_data")
    }

@app.route('/documents', methods=['GET'])
def get_all_documents():
    docs = mongo_collection.find()
    result = [document_to_json(doc) for doc in docs]
    return jsonify(result), 200

@app.route('/documents/<string:id>', methods=['GET'])
def get_document_by_id(id):
    try:
        doc = mongo_collection.find_one({"_id": ObjectId(id)})
        if doc:
            return jsonify(document_to_json(doc)), 200
        else:
            return jsonify({"error": "Document not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/documents/keyword', methods=['GET'])
def get_documents_by_keyword():
    keyword = request.args.get('keyword')
    docs = mongo_collection.find({"keyword": keyword})
    result = [document_to_json(doc) for doc in docs]
    return jsonify(result), 200

@app.route('/documents/url', methods=['GET'])
def get_documents_by_url():
    url = request.args.get('url')
    doc = mongo_collection.find_one({"url": url})
    if doc:
        return jsonify(document_to_json(doc)), 200
    else:
        return jsonify({"error": "Document not found"}), 404

@app.route('/documents/metadata', methods=['GET'])
def get_documents_by_metadata():
    title = request.args.get('title')
    description = request.args.get('description')
    query = {}
    if title:
        query["meta_data.Title"] = title
    if description:
        query["meta_data.Description"] = description
    
    docs = mongo_collection.find(query)
    result = [document_to_json(doc) for doc in docs]
    return jsonify(result), 200

#===================== Frontend routing =====================
@app.route('/')
def index():
    documents = mongo_collection.find()
    return render_template('index.html', documents=documents)

@app.route('/launch-pipeline')
def launch_pipeline():
    return render_template('launch_pipeline.html')

@app.route('/document/<doc_id>')
def document(doc_id):
    document = mongo_collection.find_one({'_id': ObjectId(doc_id)})
    return render_template('document.html', document=document)

if __name__ == '__main__':
    app.run(debug=True)
