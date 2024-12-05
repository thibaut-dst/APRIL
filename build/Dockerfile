# Utiliser une image officielle Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers dans l'image
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY functions/ functions/
COPY templates/ templates/
COPY static/ static/
COPY Vocabulaire_Expert_CSV.csv Vocabulaire_Expert_CSV.csv

RUN pip install --no-cache-dir -r requirements.txt
RUN python3 -m spacy download fr_core_news_lg
RUN apt-get update && apt-get install -y iputils-ping
RUN touch pipeline.log

# Exposer le port de l'API Flask
EXPOSE 5000

# Lancer Flask en mode développement
CMD ["python", "app.py"]
