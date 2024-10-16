import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import shutil  # To save the PDF file locally

# Function for meta scraping
def meta_scraping(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    meta_info = "META SCRAPING RESULT:\n"
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all meta tags and append their 'name' or 'http-equiv' and 'content' to meta_info
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('http-equiv')
            content = tag.get('content')
            if name and content:
                meta_info += f"{name}: {content}\n"
        
        # Extract the title separately and append it to meta_info
        title = soup.find('title').get_text() if soup.find('title') else 'No title'
        meta_info += f"Title: {title}\n"
    else:
        meta_info += f"Failed to retrieve the webpage. Status code: {response.status_code}\n"

    return meta_info

# Function to check for keyword presence in HTML content
def contains_keywords(content, keyword):
    return keyword.lower() in content.lower()

# Function to download PDF files
def download_pdfs(soup, directory, index, keyword):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Find all <a> tags that have href attribute ending with '.pdf'
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
    
    for i, link in enumerate(pdf_links):
        # If the link is relative, we need to convert it to an absolute URL
        pdf_url = link if link.startswith('http') else f"{url}/{link}"
        
        try:
            # Send a GET request to fetch the PDF
            pdf_response = requests.get(pdf_url, stream=True)
            pdf_response.raise_for_status()
            
            # Define the path for saving the PDF
            pdf_name = f"{directory}/pdf_{index}_{keyword.replace(' ', '_')}_{i}.pdf"
            
            # Write the PDF file to the directory
            with open(pdf_name, 'wb') as f:
                shutil.copyfileobj(pdf_response.raw, f)
                
            print(f"PDF downloaded: {pdf_name}")
        except Exception as e:
            print(f"Failed to download PDF from {pdf_url}: {e}")

# Google search and scraping function
def scrape_webpages(keywords_df):
    for index, row in keywords_df.iterrows():
        # Extract keywords separated by commas
        keywords = [kw.strip() for kw in row['Keywords'].split(',')]
        
        # For each individual keyword
        for keyword in keywords:
            print(f"Recherche Google effectuée avec : {keyword}")  # Show the Google search term

            # Use the keyword to perform a Google search (max 5 results per search)
            for url in search(keyword, num_results=5):  # Limit to 5 results
                try:
                    # Fetch the HTML page
                    response = requests.get(url)
                    response.raise_for_status()
                    
                    try:
                        # Parse the HTML content
                        soup = BeautifulSoup(response.text, 'html.parser')
                        content = soup.get_text()
                        
                        # Check if the keyword is in the page content
                        if contains_keywords(content, keyword):
                            # Get meta scraping result
                            meta_info = meta_scraping(url)
                            
                            # Combine the meta info and the HTML content
                            combined_content = f"<!-- {meta_info} -->\n{response.text}"
                            
                            # Save the HTML page if it contains the keyword
                            file_name = f"html_pages/page_{index}_{keyword.replace(' ', '_')}.html"
                            with open(file_name, 'w', encoding='utf-8') as file:
                                file.write(combined_content)
                            print(f"Page HTML sauvegardée : {file_name}")
                            
                            # Download any PDF documents found on the page
                            pdf_directory = "pdf_documents"
                            download_pdfs(soup, pdf_directory, index, keyword)
                            
                        else:
                            print(f"Aucun mot-clé trouvé dans la page {url}")
                    except Exception as e:
                        print(f"Erreur d'analyse du contenu HTML pour la page {url}: {e}")
                        
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
    




