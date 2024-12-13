from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Blueprint, current_app, render_template

filters = Blueprint('filters', __name__)


@filters.route('/search-documents', methods=['POST'])
def search_documents():
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents

    data = request.json
    query = {}

    # Construire la requête MongoDB
    and_conditions = []

    # Recherche dans 'keyword' pour les mots de localisation et d'analyse
    if 'keyword' in data and data['keyword']:
        words = data['keyword'].split()  # Divise par mot clé si nécessaire
        for word in words:
            and_conditions.append({"keyword": {"$regex": word, "$options": "i"}})

    if 'location' in data and data['location']:
        words = data['location'].split()  # Divise par mot clé si nécessaire
        for word in words:
            and_conditions.append({"keyword": {"$regex": word, "$options": "i"}})

    # Ajoutez la condition combinée dans la requête principale
    if and_conditions:
        query = {"$and": and_conditions}

    # Recherche dans 'Title_updated' (si fourni)
    if 'title' in data and data['title']:
        query["Title_updated"] = {"$regex": data['title'], "$options": "i"}

    # Afficher la requête dans la console pour debug
    print("Requête envoyée à MongoDB:", query, flush=True)

    # Chercher les documents correspondants
    try:
        documents = list(mongo_collection.find(query, {'_id': 0, 'Title_updated': 1, 'domain': 1, 'keyword': 1}))
        print(f"Documents trouvés: {len(documents)}", flush=True)
        return jsonify(documents)
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}", flush=True)
        return jsonify({"error": str(e)}), 500

