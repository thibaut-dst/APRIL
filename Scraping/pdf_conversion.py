import fitz  # PyMuPDF for PDF to text conversion

# Function to download and convert PDF files to TXT
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

# Function to convert PDF to text
def pdf_to_text(pdf_path, txt_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text += page.get_text("text")  # Extract plain text from each page

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
