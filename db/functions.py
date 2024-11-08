from pymongo import MongoClient

def create_mongo_collection():
    # Connexion au serveur MongoDB local
    client = MongoClient('mongodb://localhost:27017/')
    
    # Créer une base de données (si elle n'existe pas déjà)
    db = client["April"]
    
    # Créer une collection (si elle n'existe pas déjà)
    collection = db["Documents"]
    
    print(f"La collection Documents dans la base de données April a été créée (ou existe déjà).")
    