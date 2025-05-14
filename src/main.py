import csv
import json
import os
from datetime import datetime

from test_embedding import find_best_matched_category_semantic, cache_category_embeddings, load_category_embeddings
from test_fuzzy import find_best_matched_category_fuzzy


# def find_best_matched_category(sku_data, category_tree, min_depth=3):
#
#

if __name__ == "__main__":
    input_file = input("Enter the input file: ") or 'input_primary_category_verify.csv'
    override_file = input("Enter the override category file: ") or 'override_primary_category_6.csv'
    output_filename_suffix = input("Enter the output filename suffix: ") or ''

    min_depth = 3
    input_file = 'data/' + input_file

    output_file = 'output/' + datetime.now().strftime('%Y%m%d_%H%M') + '_output_matched_' + output_filename_suffix + '_' + input_file.split('/')[-1]

    print("Input file:", input_file)
    print("Minimum depth:", min_depth)
    print("Output file:", output_file)

    with open('public-category.json', 'r') as file:
        categories = json.load(file)[0]  # Assuming the first element is the category tree

    cache_file = 'category_embeddings.pkl'
    if not os.path.exists(cache_file):
        cache_category_embeddings(categories, cache_file)

    category_embeddings = load_category_embeddings(cache_file)

    # Load override data into a dictionary
    with open('data/' + override_file, 'r') as override_file:
        override_reader = csv.DictReader(override_file)
        override_dict = {row['sku']: row['primary_category'] for row in override_reader}

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['sku', 'primary_category', 'attribute_set', 'customer_segment', 'fuzzy_matched_category', 'fuzzy_matched_score',
                      'semantic_matched_category', 'semantic_matched_score',
                      'current_item_category_group', 'name', 'description']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            sku_data = {key: value for key, value in row.items()}
            sku = sku_data.get('sku', '')

            # Override primary_category if an override exists for the SKU
            if sku in override_dict:
                sku_data['primary_category'] = override_dict[sku]

            matched_category, score = find_best_matched_category_fuzzy(sku_data, categories, min_depth)
            semantic_matched_category, semantic_score = [], 0

            if (score < 100):
                semantic_matched_category, semantic_score = find_best_matched_category_semantic(
                    sku_data, category_embeddings, min_depth)
                # print(f"Fuzzy matched category: {sku} : {matched_category}, Score: {score}")
                # print(f"Semantic matched category: {sku} : {semantic_matched_category}, Score: {semantic_score}")

            matched_category_str = " > ".join(matched_category) if matched_category else "No Match Found"
            semantic_matched_category_str = " > ".join(semantic_matched_category) if semantic_matched_category else ""

            rowsValues = {field: sku_data.get(field, '') for field in fieldnames}
            writer.writerow({
                **rowsValues,
                'fuzzy_matched_category': matched_category_str,
                'fuzzy_matched_score': score,
                'semantic_matched_category': semantic_matched_category_str,
                'semantic_matched_score': semantic_score
            })
