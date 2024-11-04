import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import json
import re
from pymongo import MongoClient

# Function for meta scraping
def meta_scraping(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraction des métadonnées
        title = soup.find('title').get_text() if soup.find('title') else 'No title'
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'No description'
        og_title = soup.find('meta', property='og:title')
        og_title = og_title['content'] if og_title else 'No Open Graph title'
        og_description = soup.find('meta', property='og:description')
        og_description = og_description['content'] if og_description else 'No Open Graph description'
        canonical = soup.find('link', rel='canonical')
        canonical = canonical['href'] if canonical else 'No canonical URL'

        # Données structurées (author et date)
        structured_data = soup.find('script', type='application/ld+json')
        author = 'No author'
        date_published = 'No datePublished'

        if structured_data:
            try:
                json_data = json.loads(structured_data.string)
                if isinstance(json_data, dict):
                    author_data = json_data.get('author')
                    
                    if isinstance(author_data, dict):
                        author = author_data.get('name', 'No author')
                    date_published = json_data.get('datePublished', 'No datePublished')
            except json.JSONDecodeError as e:
                print(f"Erreur lors du décodage du JSON-LD : {e}")

        # Retourner les informations sous forme de dictionnaire
        return {
            "Title": title,
            "Description": description,
            "Open Graph Title": og_title,
            "Open Graph Description": og_description,
            "Canonical URL": canonical,
            "Author": author,
            "Date Published": date_published
        }
    else:
        print(f"Échec de la récupération de la page. Code de statut : {response.status_code}")
        return None

# Utility function to find date in text
def find_date_in_text(text):
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2} [A-Za-z]+ \d{4})'
    matches = re.findall(date_pattern, text)
    return matches[0] if matches else None

# Function to extract text from HTML content
def contains_keywords(content, keyword):
    return keyword.lower() in content.lower()

# Function to download PDF files (if needed, this can be omitted if you only want text)
def download_pdfs(soup, directory, index, keyword, url):  
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
    
    for i, link in enumerate(pdf_links):
        pdf_url = link if link.startswith('http') else f"{url}/{link}"
        try:
            pdf_response = requests.get(pdf_url, stream=True)
            pdf_response.raise_for_status()
            pdf_name = f"{directory}/pdf_{index}_{keyword.replace(' ', '_')}_{i}.pdf"
            with open(pdf_name, 'wb') as f:
                shutil.copyfileobj(pdf_response.raw, f)
            print(f"PDF downloaded: {pdf_name}")
        except Exception as e:
            print(f"Failed to download PDF from {pdf_url}: {e}")

# Google search and scraping function
def scrape_webpages_to_db(keywords_df):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['April']  # Remplacez par le nom de votre base de données
    collection = db['Documents']  # Remplacez par le nom de votre collection
    for index, row in keywords_df.iterrows():
        keywords = [kw.strip() for kw in row['Keywords'].split(',')]
        
        for keyword in keywords:
            print(f"Recherche Google effectuée avec : {keyword}")

            # Google search avec le mot-clé
            for url in search(keyword, num_results=5):  # Limité à 5 résultats
                try:
                    response = requests.get(url)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')
                    content = soup.get_text()  # Extraire le texte brut

                    # Vérifier si le mot-clé est dans le contenu
                    if contains_keywords(content, keyword):
                        # Collecter les données à insérer dans la base de données
                        page_data = {
                            "url": url,
                            "keyword": keyword,
                            "content": content,
                            "meta_data": meta_scraping(url)  # Appel à la fonction meta_scraping pour ajouter des méta-données
                        }

                        # Insertion dans la base de données MongoDB
                        collection.insert_one(page_data)
                        print(f"Page {url} enregistrée dans la base de données.")

                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors de l'accès à la page {url}: {e}")


def load_keywords(file_path):
    """
    Charge les mots-clés à partir d'un fichier CSV.
    
    Args:
        file_path (str): Le chemin vers le fichier CSV contenant les mots-clés.
        
    Returns:
        pd.DataFrame: Un DataFrame contenant les mots-clés du fichier CSV.
    """
    # Charger le fichier CSV dans un DataFrame
    keywords_df = pd.read_csv(file_path)
    print(f'Fichier {file_path} chargé avec succès.')
    return keywords_df