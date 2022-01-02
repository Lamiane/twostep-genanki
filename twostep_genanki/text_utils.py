import re
from .nltk_utils import jaro_winkler_similarity as word_sim


def shadowing(text, term, replacement='*', threshold=0.85):
    """in a given text replace all words that are threshold-similar to term"""
    words_to_replace = [word for word in text.split() 
                       if word_sim(letters_only(word.lower()), term.lower())>threshold]
    
    # sorting from longest to avoid subword problems:
    # text: `aus dem Haus sein`, term: `Haus`
    # words_to_replace: `aus`, `Haus`
    # without sorting we could get: `* dem H* sein`
    for word in sorted(words_to_replace, key=len, reverse=True):
        text = re.sub(word, replacement, text)
            
    return text.strip()


def letters_only(text):
    """remove non-letter characters and change accent-aware characters to their base form"""
    text = re.sub('e̱', 'e', text)
    text = re.sub('i̱', 'i', text)
    text = re.sub('ụ̈', 'ü', text)
    text = re.sub('u̱', 'u', text)
    text = re.sub('a̱', 'a', text)
    text = re.sub('[^\w|\s]', '', text)
    return text
