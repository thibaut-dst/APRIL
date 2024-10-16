from Scraping.functions import *

# Charger les mots-clés du CSV
file_path = 'cleaned_keywords.csv'
keywords_df = pd.read_csv(file_path)

# Créer un dossier pour sauvegarder les fichiers HTML
os.makedirs("html_pages", exist_ok=True)

#appel de la fonction de web scraping
scrape_webpages(keywords_df)