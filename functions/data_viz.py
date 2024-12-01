#import for the pie chart and the map
import matplotlib.pyplot as plt
from fastapi import APIRouter
from io import BytesIO
import base64
from pymongo.collection import Collection
#imports for the map only
import folium
from fastapi.responses import HTMLResponse
from bson.objectid import ObjectId
from typing import Dict, Any

# Import the `get_collection` function from your MongoDB utility file
from db import get_collection

router = APIRouter()

# Get the collection object
collection = get_collection()

##Pie chart

@router.get("/piechart")
async def generate_pie_chart():
    # Fetch all documents
    documents = collection.find()
    
    # Count the occurrences of each source
    source_counts = {}
    for doc in documents:
        source = doc.get("source", "Unknown")
        source_counts[source] = source_counts.get(source, 0) + 1

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(
        source_counts.values(),
        labels=source_counts.keys(),
        autopct='%1.1f%%',
        startangle=90
    )
    ax.axis('equal')  # Equal aspect ratio ensures a circular pie chart.

    # Save the pie chart to a BytesIO stream
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return {"image": encoded_image}


##map
@router.get("/map", response_class=HTMLResponse)
async def generate_map():
    # Fetch all documents with location metadata
    documents = collection.find({"location": {"$exists": True}})
    m = folium.Map(location=[0, 0], zoom_start=2)

    for doc in documents:
        location = doc.get("location", {})
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        if latitude and longitude:
            folium.Marker([latitude, longitude], popup=f"ID: {doc['_id']}").add_to(m)

    # Return the map as an HTML page
    return m._repr_html_()
