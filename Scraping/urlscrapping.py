import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pymongo import MongoClient
import json
import re
import shutil
import fitz  # PyMuPDF for PDF to text conversion


# Function for meta scraping
def meta_scraping(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').get_text() if soup.find('title') else 'No title'
        description = soup.find('meta', attrs={'name': 'description'})
        description = description['content'] if description else 'No description'
        og_title = soup.find('meta', property='og:title')
        og_title = og_title['content'] if og_title else 'No Open Graph title'
        og_description = soup.find('meta', property='og:description')
        og_description = og_description['content'] if og_description else 'No Open Graph description'
        canonical = soup.find('link', rel='canonical')
        canonical = canonical['href'] if canonical else 'No canonical URL'

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

def validate_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url  # Add 'https://' by default if no scheme is provided
    return url

def contains_keywords(content, keyword):
    return keyword.lower() in content.lower()

def download_pdfs(soup, directory, index, url):  
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
    
    for i, link in enumerate(pdf_links):
        pdf_url = link if link.startswith('http') else f"{url}/{link}"
        try:
            pdf_response = requests.get(pdf_url, stream=True)
            pdf_response.raise_for_status()
            pdf_name = f"{directory}/pdf_{index}_{i}.pdf"
            
            with open(pdf_name, 'wb') as f:
                shutil.copyfileobj(pdf_response.raw, f)
            print(f"PDF downloaded: {pdf_name}")
            
            txt_name = pdf_name.replace('.pdf', '.txt')
            pdf_to_text(pdf_name, txt_name)
            print(f"Converted PDF to text: {txt_name}")

            os.remove(pdf_name)
            print(f"Deleted PDF file: {pdf_name}")
        
        except Exception as e:
            print(f"Failed to download or convert PDF from {pdf_url}: {e}")

def pdf_to_text(pdf_path, txt_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text("text")

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)


def scrape_webpages_from_sources(file_path):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['April']  # Remplacez par le nom de votre base de données
    collection = db['Document2']  # Remplacez par le nom de votre collection

    # Charger le fichier CSV avec le bon séparateur
    sources_df = pd.read_csv(file_path, sep=';')
    
    # Remove leading/trailing spaces from column names and values
    sources_df.columns = sources_df.columns.str.strip()
    sources_df = sources_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Print column names to check if they are correct now
    print("Columns after stripping spaces:", sources_df.columns.tolist())

    # Vérifier que la colonne 'Source gouvernementale' existe
    if 'Source gouvernementale' not in sources_df.columns:
        print("La colonne 'Source gouvernementale' est manquante dans le fichier CSV.")
        return

    for index, row in sources_df.iterrows():
        url = row['Source gouvernementale']
        
        # Vérifier et ajouter 'https://' si nécessaire
        url = validate_url(url)
        print(f"Processing URL: {url}")

        try:
            # Vérifier si l'URL est déjà dans la base de données
            if collection.find_one({"url": url}):
                print(f"URL {url} already exists in the database, skipping.")
                continue  # Skip if URL already exists

            response = requests.get(url, timeout=10)  # Timeout pour éviter les blocages
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.get_text()  # Extract plain text

            # Collect meta data
            meta_data = meta_scraping(url)

            # Collect data to insert into the database
            page_data = {
                "url": url,
                "content": content,
                "meta_data": meta_data  # Include meta data in the document
            }

            # Insert data into MongoDB
            collection.insert_one(page_data)
            print(f"Page {url} saved to database.")

        except requests.exceptions.RequestException as e:
            # Gérer toutes les erreurs liées aux requêtes HTTP
            print(f"HTTP error for URL {url}: {e}")
            continue  # Continue to the next URL

        except Exception as e:
            # Gérer toutes les autres erreurs imprévues
            print(f"Unexpected error for URL {url}: {e}")
            continue  # Continue to the next URL


# Example of loading the CSV file and scraping webpages
file_path = "APRIL/Imput_voc/Sources.csv"  # Modify this with your actual path
scrape_webpages_from_sources(file_path)
