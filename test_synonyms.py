import csv
import json

import nltk
from fuzzywuzzy import fuzz
import re
from nltk.corpus import wordnet

nltk.download('wordnet')

def clean_text(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower())

def get_synonyms(words):
    synonyms = set()
    words = words.split()
    print("Words:", words)
    for word in words:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
    return synonyms

# read from input csv
if __name__ == "__main__":
    syms = get_synonyms("boots")
    print("Synonyms:", syms)
    exit()
