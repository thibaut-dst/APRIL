import pandas as pd

# Lire le fichier CSV
file_path = 'APRIL/Imput_voc/Sources.csv'  # Remplacez par le chemin de votre fichier CSV
sources_df = pd.read_csv(file_path, sep=';')
sources_df.columns = sources_df.columns.str.strip()

# Afficher les premières lignes du fichier CSV pour vérifier les colonnes
print(sources_df.head())

# Afficher les noms des colonnes
print(sources_df.columns)
