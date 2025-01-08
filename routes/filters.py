from flask import Flask, render_template, request, jsonify, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Blueprint, current_app, render_template
from functions.score_sementic import pertinence_sementic
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
        and_conditions.append({f"vocabulary_of_interest.words_of_research.{searchword1}": {"$gt": 1}})

    if 'searchword2' in data and data['searchword2']:
        searchword2 = data['searchword2']
        and_conditions.append({f"vocabulary_of_interest.words_of_research.{searchword2}": {"$gt": 1}})

    # Recherche avancée dans words_of_analysis
    if 'analyseword1' in data and data['analyseword1']:
        analyseword1 = data['analyseword1']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{analyseword1}": {"$gt": 1}})

    if 'analyseword2' in data and data['analyseword2']:
        analyseword2 = data['analyseword2']
        and_conditions.append({f"vocabulary_of_interest.words_of_analysis.{analyseword2}": {"$gt": 1}})

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

    print("condition and : " , and_conditions)
    try:
        documents = list(mongo_collection.find(query))
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])

            # Skip semantic calculation if no search words are provided
            if not any([
                data.get('searchword1'), 
                data.get('searchword2'), 
                data.get('analyseword1'), 
                data.get('analyseword2')
            ]):
                continue

            # Perform semantic calculation
            cleaned_text = doc.get('cleaned_text', '')
            mot_recherche_1 = data.get('searchword1')
            mot_recherche_2 = data.get('searchword2')
            mot_analyse_1 = data.get('analyseword1')
            mot_analyse_2 = data.get('analyseword2')

            _, semantic_score = pertinence_sementic(
                cleaned_text=cleaned_text,
                mot_recherche_1=mot_recherche_1,
                mot_recherche_2=mot_recherche_2,
                mot_analyse_1=mot_analyse_1,
                mot_analyse_2=mot_analyse_2
            )
            doc['semantic_score'] = round(semantic_score, 2)
            
        return render_template('includes/table.html', documents=documents), 200

    except Exception as e:
        print(f"Error during search: {e}", flush=True)
        return jsonify({"error": str(e)}), 500
