import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import shutil
import json
import re

# Function for meta scraping
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

        # Extract Open Graph data
        og_title = soup.find('meta', property='og:title')
        og_title = og_title['content'] if og_title else 'No Open Graph title'
        
        og_description = soup.find('meta', property='og:description')
        og_description = og_description['content'] if og_description else 'No Open Graph description'

        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        canonical = canonical['href'] if canonical else 'No canonical URL'

        # Extract structured data (author and datePublished from JSON-LD)
        structured_data = soup.find('script', type='application/ld+json')
        author = 'No author'
        date_published = 'No datePublished'

        if structured_data:
            try:
                json_data = json.loads(structured_data.string)
                if isinstance(json_data, dict):
                    author_data = json_data.get('author')
                    
                    # Handling author data based on its type
                    if isinstance(author_data, list) and len(author_data) > 0:
                        # Check if the first element is a dictionary
                        if isinstance(author_data[0], dict):
                            author = author_data[0].get('name', 'No author')
                        else:
                            author = 'No valid author found'
                    elif isinstance(author_data, dict):
                        author = author_data.get('name', 'No author')
                    elif isinstance(author_data, str):
                        author = author_data  # If it's a string, just use it directly
                    else:
                        author = 'No author'
                        
                    date_published = json_data.get('datePublished', 'No datePublished')

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON-LD data: {e}")

        # Check for other date sources
        date_tag = soup.find('small', class_='date')
        page_date = date_tag.get_text().strip() if date_tag else 'No date'

        # If no date found, look for dates in the text
        if date_published == 'No datePublished' and page_date == 'No date':
            page_text = soup.get_text()
            fallback_date = find_date_in_text(page_text)
            date_published = fallback_date if fallback_date else 'No date found'

        # Return meta information as a dictionary
        return {
            "Title": title,
            "Description": description,
            "Open Graph Title": og_title,
            "Open Graph Description": og_description,
            "Canonical URL": canonical,
            "Author": author,
            "Date Published": date_published,
            "Page Date": page_date
        }
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
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
def scrape_webpages(keywords_df):
    for index, row in keywords_df.iterrows():
        keywords = [kw.strip() for kw in row['Keywords'].split(',')]
        
        for keyword in keywords:
            print(f"Recherche Google effectuée avec : {keyword}")

            # Google search with keyword
            for url in search(keyword, num_results=5):  # Limit to 5 results
                try:
                    response = requests.get(url)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')
                    content = soup.get_text()  # Extract plain text

                    # Check if the keyword is in the plain text content
                    if contains_keywords(content, keyword):
                        # Save the plain text content
                        file_name = f"text_files/text_{index}_{keyword.replace(' ', '_')}.txt"
                        
                        if not os.path.exists('text_files'):
                            os.makedirs('text_files')
                        
                        with open(file_name, 'w', encoding='utf-8') as file:
                            file.write(content)
                        print(f"Plain text saved: {file_name}")
                        
                        # Optionally download PDFs
                        pdf_directory = "pdf_documents"
                        download_pdfs(soup, pdf_directory, index, keyword, url)
                        
                        # Call meta scraping function and save results
                        meta_info = meta_scraping(url)
                        if meta_info:
                            meta_file_name = f"text_files/meta_{index}_{keyword.replace(' ', '_')}.json"
                            with open(meta_file_name, 'w', encoding='utf-8') as meta_file:
                                json.dump(meta_info, meta_file, ensure_ascii=False, indent=4)
                            print(f"Meta info saved: {meta_file_name}")
                    else:
                        print(f"No keyword found in page {url}")

                except requests.exceptions.RequestException as e:
                    print(f"Error accessing page {url}: {e}")



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