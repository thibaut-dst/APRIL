from flask import Blueprint, jsonify, Response
from pymongo import MongoClient
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import folium

# Create a Flask Blueprint
data_viz_bp = Blueprint('data_viz', __name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["April"]  # Replace with your database name
collection = db["Documents"]  # Replace with your collection name

# ====== Pie Chart Endpoint ======
@data_viz_bp.route('/piechart', methods=['GET'])
def get_pie_chart():
    try:
        # Sample data for pie chart
        data = {"Canonical URL": 40, "Others": 60}
        labels = data.keys()
        sizes = data.values()

        # Generate the pie chart
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')

        # Save the chart to a buffer
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        # Encode the pie chart as Base64
        encoded_image = base64.b64encode(buf.read()).decode("utf-8")
        return jsonify({"image": encoded_image})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ====== Map Endpoint ======
@data_viz_bp.route('/map', methods=['GET'])
def generate_map():
    try:
        # Fetch all documents with location metadata
        documents = collection.find({"location": {"$exists": True}})
        m = folium.Map(location=[0, 0], zoom_start=2)

        for doc in documents:
            location = doc.get("location", {})
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            if latitude and longitude:
                folium.Marker([latitude, longitude], popup=f"ID: {doc['_id']}").add_to(m)

        # Convert the map to HTML
        map_html = m._repr_html_()
        return Response(map_html, content_type='text/html')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
