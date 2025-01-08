from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Blueprint, current_app, render_template

filters = Blueprint('filters', __name__)


# Build query conditions (similar to your original logic)
@filters.route('/search-table', methods=['POST'])
def search_table():
    mongo = current_app.mongo
    mongo_collection = mongo.db.Documents

    data = request.json
    query = {}
    and_conditions = []



    if 'location' in data and isinstance(data['location'], str) and data['location'].strip():
        and_conditions.append({"localisation of scraping": {"$regex": data['location'], "$options": "i"}})


    # Recherche avancée dans words_of_research
    if 'searchword1' in data and data['searchword1']:
        searchword1 = data['searchword1']
        and_conditions.append({f"vocabulary_of_interest.words_of_research.{searchword1}": {"$gt": 0}})

    if 'searchword2' in data and data['searchword2']:
        searchword2 = data['searchword2']
        and_conditions.append({f"vocabulary_of_interest.words_of_research.{searchword2}": {"$gt": 0}})

    # Recherche avancée dans words_of_analysis
    if 'analyseword1' in data and data['analyseword1']:
        analyseword1 = data['analyseword1']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{analyseword1}": {"$gt": 0}})

    if 'analyseword2' in data and data['analyseword2']:
        analyseword2 = data['analyseword2']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{analyseword2}": {"$gt": 0}})

    # Recherche par titre (Title_updated)
    if 'title' in data and isinstance(data['title'], str) and data['title'].strip():
        title = data['title'].strip()
        and_conditions.append({"Title_updated": {"$regex": title, "$options": "i"}})

    # Gestion du tag
    if 'tag' in data and data['tag']:  # Vérifie que le tag existe ET n'est pas vide
        tag_mapping = {"none": 0, "valid": 1, "wrong": 2}
        tag_value = tag_mapping.get(data['tag'], None)  # None pour une valeur invalide ou vide

        # Appliquer uniquement si une valeur valide est sélectionnée
        if tag_value is not None:
            and_conditions.append({"tagged": tag_value})




    if and_conditions:
        query = {"$and": and_conditions}

    print("final query " , query, flush=True)
    try:
        documents = list(mongo_collection.find(query))
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return render_template('includes/table.html', documents=documents), 200

    except Exception as e:
        print(f"Error during search: {e}", flush=True)
        return jsonify({"error": str(e)}), 500
