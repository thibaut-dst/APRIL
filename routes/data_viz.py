from flask import Blueprint, jsonify, Response
from flask import Blueprint, render_template
from pymongo import MongoClient
from io import BytesIO
import base64
# import matplotlib
# matplotlib.use('Agg')  # Use a non-GUI backend
# import matplotlib.pyplot as plt
#import folium
import plotly.graph_objects as go
from plotly.io import to_html


# Create a Flask Blueprint
data_viz_bp = Blueprint('data_viz', __name__)

# MongoDB setup
client = MongoClient("mongodb://mongo:27017/")
db = client["April"]  
collection = db["Documents"]

# ====== Pie Chart Endpoint ======
@data_viz_bp.route('/piechart', methods=['GET'])
def get_pie_chart_data():
    try:
        # Fetch all documents and count occurrences of each "Canonical URL"
        documents = collection.find({}, {"domain": 1, "_id": 0})  # Replace `collection` with your actual MongoDB collection
        URL_counts = {}

        # Count occurrences of each URL
        for doc in documents:
            URL = doc.get("domain", "Unknown")  # Default to "Unknown" if URL is missing
            URL_counts[URL] = URL_counts.get(URL, 0) + 1

        # Prepare data for the pie chart
        labels = list(URL_counts.keys())
        sizes = list(URL_counts.values())

        # If there is no data, return an error response
        if not sizes:
            return jsonify({"error": "No data available for domain"}), 404

        # Return labels and sizes in JSON format
        return jsonify({"labels": labels, "sizes": sizes})

    except Exception as e:
        # Catch and return any error that occurs during processing
        return jsonify({"error": str(e)}), 500


# ====== Map Endpoint ======
# @data_viz_bp.route('/map', methods=['GET'])
# def generate_map():
#     try:
#         # Fetch all documents with location metadata
#         documents = collection.find({"location": {"$exists": True}})
#         m = folium.Map(location=[0, 0], zoom_start=2)

#         for doc in documents:
#             location = doc.get("location", {})
#             latitude = location.get("latitude")
#             longitude = location.get("longitude")
#             if latitude and longitude:
#                 folium.Marker([latitude, longitude], popup=f"ID: {doc['_id']}").add_to(m)

#         # Convert the map to HTML
#         map_html = m._repr_html_()
#         return Response(map_html, content_type='text/html')
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500