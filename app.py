from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import threading
import os
import subprocess
from functions.data_viz import data_viz_bp  # Import the blueprint

app = Flask(__name__)

#===================== Database config =====================

app.config["MONGO_URI"] = "mongodb://localhost:27017/April"
mongo = PyMongo(app)
mongo_collection = mongo.db.Documents

#===================== Pipeline config =====================

# Global variable to track the process
pipeline_process = None

@app.route('/get-doc-count', methods=['GET'])
def get_doc_count():
    count = mongo_collection.count_documents({})
    return jsonify({'count': count})

""" 
def log_pipeline_output(process):
    with open('pipeline.log', 'a') as log_file:
        for line in iter(process.stdout.readline, ''):
            log_file.write(line)
            log_file.flush()
        for line in iter(process.stderr.readline, ''):
            log_file.write(f"ERROR: {line}")
            log_file.flush()
            

@app.route('/start-pipeline', methods=['POST'])
def start_pipeline():
    global pipeline_process
    if pipeline_process and pipeline_process.poll() is None:
        return "Pipeline is already running.", 400

    try:
        # Start the process and capture both stdout and stderr
        pipeline_process = subprocess.Popen(
            ['python3', 'main.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )

        # Start a thread to handle logging in the background
        threading.Thread(target=log_pipeline_output, args=(pipeline_process,), daemon=True).start()

        return "Pipeline started."
    except Exception as e:
        with open('pipeline.log', 'a') as log_file:
            log_file.write(f"Failed to start pipeline: {str(e)}\n")
        return f"Failed to start pipeline: {str(e)}", 500
 """

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
            ['python3', 'main.py'],
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

    pipeline_process.terminate()
    pipeline_process = None
    return "Pipeline stopped."


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
    app.run(debug=True)