from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Blueprint, current_app, render_template

filters = Blueprint('filters', __name__)


@filters.route('/search-table', methods=['POST'])
def search_table():
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents

    data = request.json
    query = {}
    and_conditions = []

    # Recherche par mot-clé dans Title_updated
    if 'keyword' in data and data['keyword']:
        words = data['keyword'].split()
        for word in words:
            and_conditions.append({"Title_updated": {"$regex": word, "$options": "i"}})

    # Recherche par localisation
    if 'location' in data and data['location']:
        words = data['location'].split()
        for word in words:
            and_conditions.append({"localisation of scraping": {"$regex": word, "$options": "i"}})

    # Recherche dans vocabulary_of_interest.words_of_research (analysis1 et analysis3)
    if 'analysis1' in data and data['analysis1']:
        word_of_research = data['analysis1']
        and_conditions.append({f"vocabulary_of_interest.words_of_research.{word_of_research}": {"$gt": 0}})

    if 'analysis3' in data and data['analysis3']:
        word_of_research = data['analysis3']
        and_conditions.append({f"vocabulary_of_interest.words_of_research.{word_of_research}": {"$gt": 0}})

    # Recherche dans vocabulary_of_interest.words_of_analysis (analysis2 et analysis4)
    if 'analysis2' in data and data['analysis2']:
        word_of_analysis = data['analysis2']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{word_of_analysis}": {"$gt": 0}})

    if 'analysis4' in data and data['analysis4']:
        word_of_analysis = data['analysis4']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{word_of_analysis}": {"$gt": 0}})

    # Construction de la requête avec $and si nécessaire
    if and_conditions:
        query = {"$and": and_conditions}

    try:
        # Exécuter la requête dans la base MongoDB
        documents = list(mongo_collection.find(query))

        # Convertir les ObjectId en chaînes pour éviter les problèmes de sérialisation
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

        # Rendre le tableau avec les résultats
        return render_template('includes/table.html', documents=documents), 200

    except Exception as e:
        # Gestion des erreurs
        print(f"Error during search: {e}", flush=True)
        return jsonify({"error": str(e)}), 500



""" 
@filters.route('/search-documents', methods=['POST'])
def search_documents():
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents

    data = request.json
    print("Received data:", data)

    query = {}

    # Construire la requête MongoDB
    and_conditions = []

    # Recherche dans 'keyword' pour les mots de localisation et d'analyse
    if 'keyword' in data and data['keyword']:
        words = data['keyword'].split()  # Divise par mot clé si nécessaire
        for word in words:
            and_conditions.append({"keyword of scraping": {"$regex": word, "$options": "i"}})

    if 'location' in data and data['location']:
        words = data['location'].split()  # Divise par mot clé si nécessaire
        for word in words:
            and_conditions.append({"localisation of scraping": {"$regex": word, "$options": "i"}})
    
    if 'analysis' in data and data['analysis']:
        word_of_analysis = data['analysis']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{word_of_analysis}": {"$gt": 0}})

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
        documents = list(mongo_collection.find(query))

        # Conversion des ObjectId en chaînes pour la sérialisation JSON
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])  # Convertir ObjectId en chaîne

        print(f"Documents trouvés: {len(documents)}", flush=True)
        return jsonify(documents), 200
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}", flush=True)
        return jsonify({"error": str(e)}), 500
 """