from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import threading
import os
import subprocess
import logging
app = Flask(__name__)

#===================== Database config =====================

app.config["MONGO_URI"] = "mongodb://mongo:27017/April"
mongo = PyMongo(app)
mongo_collection = mongo.db.Documents

#===================== Pipeline config =====================

# Global variable to track the process
pipeline_process = None
nlp_process = None

@app.route('/get-doc-count', methods=['GET'])
def get_doc_count():
    count = mongo_collection.count_documents({})
    return jsonify({'count': count})

@app.route('/get-doc-processed-count', methods=['GET'])
def get_doc_processed_count():
    query = {"cleaned_text": {"$exists": True}} 
    count = mongo_collection.count_documents(query) 
    return jsonify({'count': count})


def log_pipeline_output(process):
    with open('pipeline.log', 'a') as log_file:
        try:
            # Continuously read from stdout and stderr
            while True:
                # Read a line from stdout
                line = process.stdout.readline()
                if not line:  # Stop if the stream is closed
                    break
                log_file.write(line)  # Log the output
                log_file.flush()

            # Handle stderr similarly
            while True:
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
        # Start the process and capture both stdout and stderr
        pipeline_process = subprocess.Popen(
            ['python3', 'functions/launch_pipeline1.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )

        # Start a thread to handle logging in the background
        log_thread = threading.Thread(target=log_pipeline_output, args=(pipeline_process,), daemon=True)
        log_thread.start()

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

    # Log that the pipeline is being stopped
    with open('pipeline.log', 'a') as log_file:
        log_file.write("Pipeline is being stopped by user.\n")

    pipeline_process.terminate()
    pipeline_process = None

    # Log after the pipeline is successfully stopped
    with open('pipeline.log', 'a') as log_file:
        log_file.write("Pipeline has been successfully stopped.\n")

    return "Pipeline stopped."

@app.route('/run-nlp', methods=['POST'])
def run_nlp():
    global nlp_process
    if nlp_process and nlp_process.poll() is None:
        return "NLP is already running.", 400

    try:
        nlp_process = subprocess.Popen(
            ['python3', 'functions/launch_pipeline2.py'],  # Ensure this runs the NLP processing script
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )

        log_thread = threading.Thread(target=log_pipeline_output, args=(nlp_process,), daemon=True)
        log_thread.start()

        return "NLP processing started."

    except Exception as e:
        logging.error(f"Failed to start NLP processing: {str(e)}")
        return f"Failed to start NLP processing: {str(e)}", 500




@app.route('/get-logs', methods=['GET'])
def get_logs():
    log_file = 'pipeline.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()
        return jsonify({'logs': logs[-20:]})  # Return the last 20 lines of logs
    else:
        return jsonify({'logs': []})


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


# Register the data visualization blueprint
app.register_blueprint(data_viz_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
