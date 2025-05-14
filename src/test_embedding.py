import csv
import json
import os
import pickle
import time

from sentence_transformers import SentenceTransformer, util

from test_utility import clean_text, build_combined_input

# Load the model
model = SentenceTransformer('all-MiniLM-L6-v2')


def cache_category_embeddings(category_tree, cache_file='category_embeddings.pkl'):
    """Precompute and cache embeddings for the category tree."""

    def traverse_tree(tree, path, embeddings):
        for category in tree:
            current_path = path + [category["label"]]
            combined_category = " > ".join(current_path).lower()
            embeddings[combined_category] = model.encode(combined_category, convert_to_tensor=True)
            if "children" in category:
                traverse_tree(category["children"], current_path, embeddings)

    embeddings = {}
    traverse_tree(category_tree, [], embeddings)
    with open(cache_file, 'wb') as f:
        pickle.dump(embeddings, f)

    print(f"Category embeddings cached to {cache_file}")


def load_category_embeddings(cache_file='category_embeddings.pkl'):
    """Load cached embeddings from a file."""
    with open(cache_file, 'rb') as f:
        return pickle.load(f)


def find_best_matched_category_semantic(sku_data, category_embeddings, min_depth=3):
    combined_input = build_combined_input(sku_data)
    print(f"Combined input: {combined_input}")

    input_embedding = model.encode(combined_input, convert_to_tensor=True)
    # Define weights for each level
    level_weights = {1: 5, 2: 4, 3: 3}
    default_weight = 0.5  # Levels 4+ have a lighter weight

    matches = []
    for category_path, category_embedding in category_embeddings.items():
        similarity = util.pytorch_cos_sim(input_embedding, category_embedding).item()
        # Calculate weighted importance score
        score = similarity * 100

        for i, level in enumerate(category_path.split(' > '), start=1):
            weight = level_weights.get(i, default_weight)
            score += weight * similarity

        category_lv = len(category_path.split(' > '))

        if category_lv == 2 and sku_data.get('attribute_set', '').lower() in category_path:
            score += 5
        if category_lv == 1 and sku_data.get('customer_segment', '').lower() in category_path:
            score += 5

        matches.append((category_path.split(' > '), score))

    matches.sort(key=lambda x: x[1], reverse=True)
    # Get the top 5 matches
    # top_matches = matches[:5]

    # for match, score in top_matches:
    #     print(f"Match: {' > '.join(match)}, Score: {score}")

    for match, score in matches:
        if len(match) >= min_depth:
            return [match, score]
    return ["Unknown"] * min_depth, 0


if __name__ == "__main__":
    min_depth = 3
    start_full_time = time.time()  # Start timing

    input_file = 'data/input_primary_category_verify_single.csv'
    cache_file = 'category_embeddings.pkl'

    with open('public-category.json', 'r') as file:
        categories = json.load(file)[0]  # Assuming the first element is the category tree

    if not os.path.exists(cache_file):
        cache_category_embeddings(categories, cache_file)

    category_embeddings = load_category_embeddings(cache_file)

    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            start_time = time.time()  # Start timing

            sku_data = {key: value for key, value in row.items()}
            sku = sku_data.get('sku', '')

            semantic_matched_category, semantic_score = find_best_matched_category_semantic(sku_data, category_embeddings, min_depth)

            print(f"Semantic matched category: {sku} : {semantic_matched_category}, Score: {semantic_score}")
            end_time = time.time()
            total_time = end_time - start_time
            print(f"Time taken: {total_time:.4f} seconds")

    end_full_time = time.time()  # End timing
    total_full_time = end_full_time - start_full_time
    print(f"Total time taken: {total_full_time:.4f} seconds")
