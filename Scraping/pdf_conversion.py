import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from googlesearch import search
import shutil
import json
import re
import fitz 

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
            
            # Save the PDF file
            with open(pdf_name, 'wb') as f:
                shutil.copyfileobj(pdf_response.raw, f)
            print(f"PDF downloaded: {pdf_name}")
            
            # Convert PDF to TXT
            txt_name = pdf_name.replace('.pdf', '.txt')
            pdf_to_text(pdf_name, txt_name)
            print(f"Converted PDF to text: {txt_name}")
        
        except Exception as e:
            print(f"Failed to download or convert PDF from {pdf_url}: {e}")

def pdf_to_text(pdf_path, txt_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text("text")  # Extract plain text from each page

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

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

