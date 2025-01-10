import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import spacy
nlp = spacy.load("fr_core_news_lg") 

import logging

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

        if len(words_not_none) == 0:    
            return 0 , 0
        else :
            # Generate cleaning and embedding for the text
            doc = nlp(cleaned_text)
            filtered_tokens = [token.text for token in doc if not token.is_punct and not token.is_stop]
            cleaned_text_filtered = " ".join(filtered_tokens)

            text_embedding = model.encode([cleaned_text_filtered])                                                 # A lightweight SBERT model


            similarity_score = {}
            for word in words_not_none:
                
                # Generate embedding for the word
                word_embedding = model.encode([word])              # A lightweight SBERT model

                # Calculate cosine similarity
                similarity = cosine_similarity(word_embedding, text_embedding)          # A lightweight SBERT model


                similarity_score[word] = similarity[0][0]
            score = np.mean(list(similarity_score.values()))

            return similarity_score, score
    
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise SystemExit(f"Error processing document: {e}")
