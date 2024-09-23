import requests
from bs4 import BeautifulSoup

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

if __name__ == "__main__":
    url = "https://littoral-occitanie.fr/Presentation-202"  # Replace with the target URL
    meta_scraping(url)
