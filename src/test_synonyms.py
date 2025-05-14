import csv
import json
import nltk
from fuzzywuzzy import fuzz
import re
from nltk.corpus import wordnet
from test_utility import clean_text

nltk.download('wordnet')

MANUAL_SYNONYMS = {
    "baby": ["kid", "child"],
    "shoes": ["footwear"],
    "sandals": ["footwear"],
    "clothing": ["apparel", "clothes", "fashion"],
    # "boxers": ["underwear", "boxer shorts", "briefs", "trunks"],
    # "briefs": ["underwear", "boxers", "trunks"],
    # "panties": ["underwear"],
    # "bra": ["underwear", "lingerie"],
    # "trunks": ["underwear", "boxers"],
}



def get_synonyms(text):
    synonyms = set()
    clean_text(text)
    words = text.split()
    for word in words:
        # Add manual synonyms
        if word in MANUAL_SYNONYMS:
            synonyms.update(MANUAL_SYNONYMS[word])
        # for syn in wordnet.synsets(word):
        #     for lemma in syn.lemmas():
        #         synonyms.add(lemma.name().replace('_', ' '))

    return synonyms


if __name__ == "__main__":
    syms = get_synonyms('Clothing')

    print("Synonyms:", syms)
    exit()
