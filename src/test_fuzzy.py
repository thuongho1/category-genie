import csv
import json
import time

from fuzzywuzzy import fuzz

from test_synonyms import get_synonyms
from test_utility import clean_text, build_combined_input


def combined_fuzzy_score(input_str, category_str):
    scores = [
        fuzz.token_set_ratio(input_str, category_str),
        fuzz.token_sort_ratio(input_str, category_str),
        fuzz.partial_ratio(input_str, category_str)
    ]
    return sum(scores) / len(scores)


def find_best_matched_category_fuzzy(sku_data, category_tree, min_depth=3):
    """Fuzzy + synonym matching."""
    weights = {
        'primary_category': 5,
        'attribute_set': 5,
        'customer_segment': 3,
        'name': 2,
        'gender': 1,
        # 'description': 1,
    }
    # Define weights for each level
    level_weights = {1: 3, 2: 2, 3: 1}
    default_weight = 0.5  # Levels 4+ have a lighter weight

    combined_input = build_combined_input(sku_data, weights)
    primary_category = sku_data.get('primary_category', '')
    primary_category = primary_category.replace('Root Category##', '')
    primary_category = primary_category.replace('##', ' ').lower()

    primary_category = primary_category.split('##', 1)[-1]

    # print("Primary Category:", primary_category)
    # Gather all words from name and primary_category for synonym expansion
    name_words = clean_text(sku_data.get('name', ''))
    primary_category_words = clean_text(sku_data.get('primary_category', '').split(' ')[-1])
    segment = clean_text(sku_data.get('customer_segment', ''))
    # all_words = set(name_words.split() + primary_category_words.split() + segment.split())
    all_words = set(primary_category.split())
    # print("All Words:", all_words)
    synonyms = set()
    for word in all_words:
        synonyms.update(get_synonyms(word))
    # print("synonyms:", synonyms)
    # Add synonyms to the input for fuzzy matching
    combined_input = combined_input + ' ' + ' '.join(synonyms)

    def traverse_tree(tree, path):
        matches = []
        for category in tree:
            current_path = path + [category["label"]]
            combined_category = clean_text(" > ".join(current_path).lower())
            score = fuzz.token_set_ratio(combined_input, combined_category)

            category_lv = len(current_path)

            # Boosts
            # if category_lv == 1 and sku_data.get('customer_segment', '').lower() in combined_category:
            #     score += 5
            # if category_lv == 2 and sku_data.get('attribute_set', '').lower() in combined_category:
            #     score += 5

            if sku_data.get('attribute_set', '').lower() in combined_category:
                score += 5
            # if any(syn in combined_category for syn in synonyms):
            #     score += 10

            if ("kids" in combined_category) and combined_input not in ["kids", "kid"]:
                score -= 10

            matches.append((current_path, score))
            if "children" in category:
                matches.extend(traverse_tree(category["children"], current_path))
        return matches

    all_matches = traverse_tree(category_tree, [])
    all_matches.sort(key=lambda x: x[1], reverse=True)
    #  get 5 best matches
    # all_matches = all_matches[:10]
    # print("All Matches:", all_matches)

    for match, score in all_matches:
        if len(match) >= min_depth:
            return [match, score]
    return ["Unknown"] * min_depth, 0


if __name__ == "__main__":
    min_depth = 3
    all_start_time = time.time()  # Start timing

    # Load category tree
    with open('public-category.json', 'r') as file:
        categories = json.load(file)[0]  # Assuming the first element is the category tree

    # Input file
    input_file = 'data/input_primary_category_verify_single.csv'

    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            start_time = time.time()  # Start timing

            sku_data = {key: value for key, value in row.items()}
            sku = sku_data.get('sku', '')

            matched_category, score = find_best_matched_category_fuzzy(sku_data, categories, min_depth)

            print(f"Matched category: {sku} : {matched_category}, Score: {score}")
            end_time = time.time()
            total_time = end_time - start_time
            print(f"Time taken: {total_time:.4f} seconds")

    all_end_time = time.time()  # End timing
    all_total_time = all_end_time - all_start_time
    print(f"Total execution time: {total_time:.2f} seconds")