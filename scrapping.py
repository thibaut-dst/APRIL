from Scraping.functions import *
from db.functions import *

create_mongo_collection()
# Charger les mots-clés du CSV
file_path = 'APRIL/cleaned_keywords.csv'
keywords_df = pd.read_csv(file_path)

# Créer un dossier pour sauvegarder les fichiers HTML
os.makedirs("html_pages", exist_ok=True)

<<<<<<< HEAD
scrape_webpages_to_db(keywords_df)
=======
scrape_webpages_to_db(keywords_df, max_links=50)
>>>>>>> ba4e6c1bd1d551498e99a02770069230789bef30
