import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import spacy
from spacy.tokens import Doc
nlp = spacy.load("fr_core_news_sm") 

import logging

#model = fasttext.load_model('functions/cc.fr.300.bin')      # Un modèle fasttext
model = SentenceTransformer('all-MiniLM-L6-v2')             # Un modèle léger de SBERT
logging.info("model load")


logging.basicConfig(
    filename='pipeline.log',       # Logs will be saved to 'pipeline.log'
    filemode='a',                  # Append to the log file
    level=logging.INFO,            # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
) 


def pertinence_sementic(cleaned_text: str , mot_recherche_1 : str = None, mot_recherche_2: str=None, 
                        mot_analyse_1: str=None , mot_analyse_2: str=None) -> float:
    """
    Calculates relevance using semantic proximity based on the words.
        
    Parameters:
        cleaned_text (str): The text to analyze.
        mot_recherche_1 (str, optional): The first search word. Defaults to None.
        mot_recherche_2 (str, optional): The second search word. Defaults to None.
        mot_analyse_1 (str, optional): The first analysis word. Defaults to None.
        mot_analyse_2 (str, optional): The second analysis word. Defaults to None.

    Returns:
        float: The semantic relevance score.
    
    """
    try:
        words_not_none = [word for word in [mot_recherche_1, mot_recherche_2, mot_analyse_1, mot_analyse_2] if word is not None]

        # Générer le nettoyage et l'embedding pour le texte
        doc = nlp(cleaned_text)
        filtered_tokens = [token.text for token in doc if not token.is_punct and not token.is_stop]
        cleaned_text_filtered = " ".join(filtered_tokens)


        #text_embedding = np.mean([model.get_word_vector(w) for w in cleaned_text_filtered.split()], axis=0)    # Un modèle fasttext
        text_embedding = model.encode([cleaned_text_filtered])                                                 # Un modèle léger de SBERT


        similarity_score = {}
        similarity_values = [] 

        for word in words_not_none:
            
            # Générer l'embedding pour le mot
            #word_embedding = model.get_word_vector(word)       # Un modèle fasttext
            word_embedding = model.encode([word])              # Un modèle léger de SBERT

            # Calculer la similarité cosinus
            #similarity = cosine_similarity([word_embedding], [text_embedding])      # Un modèle fasttext
            similarity = cosine_similarity(word_embedding, text_embedding)          # Un modèle léger de SBERT
            
            similarity_score[word] = similarity[0][0]
            similarity_values.append(similarity[0][0]) 
        score = np.mean(similarity_values)
        return similarity_score, score
    
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise SystemExit(f"Error processing document: {e}")
