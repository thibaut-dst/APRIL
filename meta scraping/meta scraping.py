import requests
from bs4 import BeautifulSoup

def meta_scraping(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all meta tags and print their 'name' or 'http-equiv' and 'content'
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            # Try to get 'name' or 'http-equiv' attribute (if they exist)
            name = tag.get('name') or tag.get('http-equiv')
            content = tag.get('content')
            
            # Only print if both name (or http-equiv) and content exist
            if name and content:
                print(f"{name}: {content}")

        # Extract the title separately
        title = soup.find('title').get_text() if soup.find('title') else 'No title'
        print(f"Title: {title}")

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

if __name__ == "__main__":
    url = "https://littoral-occitanie.fr/Presentation-202"  # Replace with the target URL
    meta_scraping(url)
