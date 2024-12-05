import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import json
import re
import logging
import fitz
from datetime import datetime  # Importing datetime module

# Function for meta scraping
def meta_scraping(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info(f"Successfully fetched page: {url}")

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
                #print(f"Erreur lors du décodage du JSON-LD : {e}")
                logging.warning(f"Error decoding JSON-LD on page {url}: {e}")

        # Get the current date and time of scraping
        date_scraped = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Retourner les informations sous forme de dictionnaire
        return {
            "Title": title,
            "Description": description,
            "Open Graph Title": og_title,
            "Open Graph Description": og_description,
            "Canonical URL": canonical,
            "Author": author,
            "Date Published": date_published,
            "Date Scraped": date_scraped 
        }
    else:
        #print(f"Échec de la récupération de la page. Code de statut : {response.status_code}")
        logging.error(f"Failed to fetch page {url}. Status code: {response.status_code}")

        return None

# Function to extract Text from HTML content
def contains_keywords(content, keyword):
    return keyword.lower() in content.lower()

# Function to transform PDF into Text 
def pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text("text")
    return text

# Function for meta scraping for the PDF file
def pdf_meta_scraping(pdf_path):
    with fitz.open(pdf_path) as doc:
        metadata = doc.metadata  
        title = metadata.get('title', 'No title')
        author = metadata.get('author', 'No author')
        created = metadata.get('creationDate', 'No creation date')

    return {
        "Title": title,
        "Author": author,
        "Creation Date": created
    }

# Function for scraping into the Database
def scrape_webpages_to_db(keywords_list, collection):
    """
    Google search and scraping function
    Supports both HTML and PDF files and stores data in MongoDB.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }    
    for index, keyword in enumerate(keywords_list):
        
        logging.info(f"Starting Google search for: '{keyword}'")
        for url in search(keyword, num_results=3):  # Limited to 3 results
            try:
                # Check if document already exists in DB
                if collection.find_one({"url": url}):
                    logging.info(f"Document already exists in DB, skipping: {url}")
                    continue

                response = requests.get(url, headers=headers)
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').lower()
                
                if 'application/pdf' in content_type:
                    file_type = "pdf"
                    pdf_name = f"temp_pdf_{index}.pdf"
                    with open(pdf_name, 'wb') as f:
                        f.write(response.content)
                    text_content = pdf_to_text(pdf_name)
                    pdf_metadata = pdf_meta_scraping(pdf_name)

                    os.remove(pdf_name)
                    page_data = {
                        "url": url,
                        "keyword": keyword,
                        "content": text_content,
                        "meta_data": {
                            "file_type": file_type,
                            "source_url": url,
                            **pdf_metadata
                        }
                    }
                    collection.insert_one(page_data)
                    logging.info(f"PDF content stored in DB from {url}.")
                    
                elif 'text/html' in content_type: # Handle HTML pages
                    file_type = "html" 
                    soup = BeautifulSoup(response.text, 'html.parser')
                    #content = soup.get_text()  # v0 du get_text

                    paragraphs = soup.find_all('p')
                    content = ""
                    for p in paragraphs:
                        content += p.get_text() + " <br> "
                    content = content.strip()

                    # Check if the keyword is present in the content
                    if contains_keywords(content, keyword):
                        page_data = {
                            "url": url,
                            "keyword": keyword,
                            "content": content,
                            "meta_data": {
                                "file_type": file_type,
                                **meta_scraping(url)
                            }
                        }
                        collection.insert_one(page_data)
                        logging.info(f"Page HTML stored in DB: {url}")

            except requests.exceptions.RequestException as e:
                logging.error(f"Error accessing page {url}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error processing {url}: {e}")
