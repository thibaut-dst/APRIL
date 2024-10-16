import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import os

def meta_scraping(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title
        title = soup.find('title').get_text() if soup.find('title') else 'No title'

        # Extract meta description
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'No description'

        # Extract Open Graph data (og:title, og:description, etc.)
        og_title = soup.find('meta', property='og:title')
        og_title = og_title['content'] if og_title else 'No Open Graph title'
        
        og_description = soup.find('meta', property='og:description')
        og_description = og_description['content'] if og_description else 'No Open Graph description'

        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Open Graph Title: {og_title}")
        print(f"Open Graph Description: {og_description}")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")


# Fonction pour vérifier la présence de mots-clés dans le contenu HTML
def contains_keywords(content, keyword):
    return keyword.lower() in content.lower()

# Fonction de recherche Google et scraping
def scrape_webpages(keywords_df):
    for index, row in keywords_df.iterrows():
        # Extraire les mots-clés séparés par des virgules
        keywords = [kw.strip() for kw in row['Keywords'].split(',')]
        
        # Pour chaque mot-clé individuel
        for keyword in keywords:
            print(f"Recherche Google effectuée avec : {keyword}")  # Afficher la recherche Google

            # Utiliser le mot-clé pour effectuer une recherche Google (max 5 résultats par recherche)
            for url in search(keyword):
                try:
                    # Faire la requête HTTP pour récupérer la page HTML
                    response = requests.get(url)
                    response.raise_for_status()
                    
                    # Analyser le contenu HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    content = soup.get_text()
                    
                    # Vérifier si le mot-clé est présent dans la page
                    if contains_keywords(content, keyword):
                        # Sauvegarder la page HTML si elle contient le mot-clé
                        file_name = f"html_pages/page_{index}_{keyword.replace(' ', '_')}.html"
                        with open(file_name, 'w', encoding='utf-8') as file:
                            file.write(response.text)
                        print(f"Page HTML sauvegardée : {file_name}")
                    else:
                        print(f"Aucun mot-clé trouvé dans la page {url}")
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
    




