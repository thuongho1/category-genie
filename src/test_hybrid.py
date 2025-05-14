import os
import csv
import json
import time

from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import util, SentenceTransformer

from test_embedding import cache_category_embeddings, load_category_embeddings
from test_utility import clean_text, build_combined_input

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


def extract_dynamic_keywords(sku_data, top_n=5):
    """Extract dynamic keywords from SKU data using TF-IDF."""
    text_data = [
        sku_data.get('name', ''),
        sku_data.get('description', ''),
        sku_data.get('attribute_set', ''),
        # sku_data.get('customer_segment', '')
    ]
    vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
    tfidf_matrix = vectorizer.fit_transform(text_data)
    return vectorizer.get_feature_names_out()


def calculate_fuzzy_score(input_str, category_path):
    """Calculate fuzzy score for a category path."""
    combined_category = clean_text(" > ".join(category_path).lower())
    return fuzz.token_set_ratio(input_str, combined_category)


def find_best_matched_category(sku_data, category_tree, min_depth=3, cache_file='category_embeddings.pkl'):
    """Unified matching logic using fuzzy, semantic similarity, and dynamic keyword extraction."""
    if not os.path.exists(cache_file):
        cache_category_embeddings(category_tree, cache_file)

    category_embeddings = load_category_embeddings(cache_file)
    combined_input = build_combined_input(sku_data)
    input_embedding = model.encode(combined_input, convert_to_tensor=True)
    # dynamic_keywords = extract_dynamic_keywords(sku_data)

    # Define weights for levels and scoring
    level_weights = {1: 5, 2: 4, 3: 3}
    default_weight = 0.5  # Levels 4+ have a lighter weight
    fuzzy_weight = 0.6  # Weight for fuzzy score
    semantic_weight = 0.7  # Weight for semantic score
    keyword_boost = 10  # Boost for matching dynamic keywords

    matches = []

    for category_path, category_embedding in category_embeddings.items():
        # Calculate semantic similarity
        semantic_similarity = util.pytorch_cos_sim(input_embedding, category_embedding).item() * 100

        # Calculate fuzzy score
        fuzzy_score = calculate_fuzzy_score(combined_input, category_path.split(' > '))

        # Boost score if dynamic keywords match the category path
        category_text = " > ".join(category_path.split(' > ')).lower()
        # keyword_boost_score = sum(1 for keyword in dynamic_keywords if keyword in category_text) * keyword_boost

        # Combine fuzzy and semantic scores
        # combined_score = (semantic_weight * semantic_similarity)
        # combined_score =  (fuzzy_weight * fuzzy_score)
        # combined_score = (fuzzy_weight * fuzzy_score) + (semantic_weight * semantic_similarity) + keyword_boost_score
        combined_score = (fuzzy_weight * fuzzy_score) + (semantic_weight * semantic_similarity)
        # Add level-based weighting
        # for i, level in enumerate(category_path.split(' > '), start=1):
        #     weight = level_weights.get(i, default_weight)
        #     combined_score += weight * semantic_similarity

        matches.append((category_path.split(' > '), combined_score))

    # Sort matches by combined score
    matches.sort(key=lambda x: x[1], reverse=True)

    # Return the highest match with the correct depth
    for match, score in matches:
        if len(match) >= min_depth:
            return [match, score]
    return ["Unknown"] * min_depth, 0


if __name__ == "__main__":
    min_depth = 3
    start_time = time.time()  # Start timing

    # Load category tree
    with open('public-category.json', 'r') as file:
        categories = json.load(file)[0]  # Assuming the first element is the category tree

    # Input file
    input_file = 'data/input_primary_category_verify_single.csv'

    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            sku_data = {key: value for key, value in row.items()}
            sku = sku_data.get('sku', '')

            matched_category, score = find_best_matched_category(sku_data, categories, min_depth)

            print(f"Matched category: {sku} : {matched_category}, Score: {score}")

    end_time = time.time()  # End timing
    total_time = end_time - start_time
    print(f"Total execution time: {total_time:.2f} seconds")