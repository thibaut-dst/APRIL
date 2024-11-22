import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import json
import re
from pymongo import MongoClient
import fitz  # PyMuPDF for PDF to text conversion
import shutil

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

def contains_keywords(content, keyword):
    return keyword.lower() in content.lower()

# Function to download PDFs and convert to text
def download_pdfs(soup, collection, index, keyword, url):
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
    
    for i, link in enumerate(pdf_links):
        pdf_url = link if link.startswith('http') else f"{url}/{link}"
        try:
            pdf_response = requests.get(pdf_url, stream=True)
            pdf_response.raise_for_status()
            pdf_name = f"temp_pdf_{index}_{i}.pdf"
            
            # Save and convert the PDF to text
            with open(pdf_name, 'wb') as f:
                shutil.copyfileobj(pdf_response.raw, f)
            text_content = pdf_to_text(pdf_name)

            # Store PDF text in MongoDB
            pdf_data = {
                "url": pdf_url,
                "keyword": keyword,
                "pdf_text_content": text_content,
                "source_url": url
            }
            collection.insert_one(pdf_data)
            print(f"PDF content from {pdf_url} saved to MongoDB.")
            
            # Clean up the PDF file after storing text
            os.remove(pdf_name)
        
        except Exception as e:
            print(f"Failed to download or convert PDF from {pdf_url}: {e}")

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text("text")
    return text

# Google search and scraping function
def scrape_webpages_to_db(keywords_df, max_links=50):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['April']
    collection = db['Documents']

    total_links_count = 0  # Global link counter

    for index, row in keywords_df.iterrows():
        keywords = [kw.strip() for kw in row['Keywords'].split(',')]

        for keyword in keywords:
            print(f"Performing Google search with: {keyword}")

            # Perform Google search
            for url in search(keyword, num_results=5):  # Limiting to 5 results per search
                if total_links_count >= max_links:
                    print(f"Reached the maximum number of links ({max_links}), stopping script.")
                    return

                try:
                    # Check if URL is already in the database
                    if collection.find_one({"url": url}):
                        print(f"URL {url} already exists in the database, skipping.")
                        continue

                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Determine file type
                    file_type = "pdf" if url.lower().endswith(".pdf") else "html"

                    if file_type == "pdf":  # Handle PDFs
                        pdf_name = f"temp_pdf_{index}.pdf"
                        with open(pdf_name, 'wb') as f:
                            f.write(response.content)
                        text_content = pdf_to_text(pdf_name)
                        os.remove(pdf_name)

                        page_data = {
                            "url": url,
                            "keyword": keyword,
                            "meta_data": {
                                "file_type": file_type,
                                "source_url": url,
                            },
                            "pdf_text_content": text_content
                        }
                        collection.insert_one(page_data)
                        print(f"PDF content from {url} saved to MongoDB.")
                        total_links_count += 1

                    else:  # Handle HTML pages
                        content = soup.get_text()

                        if contains_keywords(content, keyword):
                            page_data = {
                                "url": url,
                                "keyword": keyword,
                                "html_text_content": content,
                                "meta_data": {
                                    "file_type": file_type,
                                    **meta_scraping(url)
                                }
                            }
                            collection.insert_one(page_data)
                            print(f"HTML content from {url} saved to MongoDB.")
                            total_links_count += 1

                except requests.exceptions.RequestException as e:
                    print(f"Error accessing page {url}: {e}")
                    
# Load keywords from CSV
def load_keywords(file_path):
    keywords_df = pd.read_csv(file_path)
    print(f'Fichier {file_path} chargé avec succès.')
    return keywords_df
