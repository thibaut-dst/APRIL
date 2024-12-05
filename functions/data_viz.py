from flask import Blueprint, jsonify, Response
from pymongo import MongoClient
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend
import matplotlib.pyplot as plt
import folium
import plotly.graph_objects as go
from plotly.io import to_html


# Create a Flask Blueprint
data_viz_bp = Blueprint('data_viz', __name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["April"]  
collection = db["Documents"]  

# ====== Pie Chart Endpoint ======
@data_viz_bp.route('/piechart', methods=['GET'])
def get_pie_chart():
    try:
        # Fetch all documents and count occurrences of each "Canonical URL"
        documents = collection.find({}, {"url": 1, "_id": 0})
        URL_counts = {}

        for doc in documents:
            URL = doc.get("url", "Unknown")  # Default to "Unknown" if missing
            URL_counts[URL] = URL_counts.get(URL, 0) + 1

        # Prepare data for the pie chart
        labels = list(URL_counts.keys())
        sizes = list(URL_counts.values())

        if not sizes:
            return jsonify({"error": "No data available for url"}), 404

        # Custom function to display raw counts on the pie chart
        def absolute_value(val):
            total = sum(sizes)
            count = int(round(val * total / 100))
            return f"{count}"  # Display only the raw count

        # Generate the pie chart
        fig, ax = plt.subplots(figsize=(10, 10))  # Optional: Adjust figure size
        wedges, texts, autotexts = ax.pie(
            sizes, 
            #labels=labels, 
            autopct=absolute_value, #autopct='%1.1f%%'
            startangle=90, 
            textprops={'fontsize': 15},
            wedgeprops={'edgecolor': 'black'}
        )
        ax.axis('equal')  # Equal aspect ratio ensures a circular pie chart.

        # Add a legend using plt.legend
        plt.legend(
            wedges, 
            labels,  # Use URLs as legend labels
            title="Sources", 
            loc="center left", 
            bbox_to_anchor=(1, 0.5),  # Position legend outside the chart
            fontsize=12  # Adjust legend text size
        )

        # Save the chart to a buffer
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
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
