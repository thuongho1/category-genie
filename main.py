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
    # print("Words:", words)
    # for syn in wordnet.synsets(words):
    #     for lemma in syn.lemmas():
    #         synonyms.add(lemma.name())
    for word in words:
    #    call get_synonyms function
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
    return synonyms

def find_best_matched_category(sku_data, category_tree, min_depth=3):
    # Combine factors for comparison
    primary_category = sku_data.get('primary_category', '').replace('/', ' ')

    combined_input = ' '.join([
        primary_category,
        sku_data.get('name', ''),
        sku_data.get('attribute_set', ''),
        sku_data.get('gender', ''),
        sku_data.get('customer_segment', ''),
        sku_data.get('description', ''),
    ])

    combined_input = clean_text(combined_input)
    # # Apply synonyms to the combined input
    primary_category_words = sku_data.get('primary_category').split('/')[-1]

    synonyms = get_synonyms(primary_category_words)

    # print("Primary Category:", primary_category_words)
    # print("Synonyms:", synonyms)
    # #
    combined_input += ' '.join(synonyms)

    def traverse_tree(tree, path):
        matches = []

        for category in tree:
            current_path = path + [category["label"]]

            combined_category = " > ".join(current_path).lower()
            combined_category = clean_text(combined_category)

            score = fuzz.token_set_ratio(combined_input, combined_category)
            # Boost score for synonyms

            if any(syn in combined_category for syn in synonyms):
                score += 15

            if ("kids" in combined_category) and combined_input not in ["kids", "kid"]:
                score -= 20
            # else:
            #     score += 5


            # Get related terms for the input primary_category
            # related_terms = type_mapping.get(primary_category.lower(), []) if type_mapping else []
            # print("Matching terms:", related_terms)

            # # Calculate relevance score based on related terms
            # if related_terms:
            #     matching_terms = [term for term in related_terms if term in combined_category]
            #     relevance_score = len(matching_terms) / len(related_terms) * 20  # Adjust weight as needed
            #     score += relevance_score
            #
            #     # Penalize if no related terms match
            #     if not matching_terms:
            #         score -= 20  # Adjust penalty value as needed

            matches.append((current_path, score))

            # Recursively check children
            if "children" in category:
                matches.extend(traverse_tree(category["children"], current_path))

        return matches

    # Get all matches with scores
    all_matches = traverse_tree(category_tree, [])

    # Sort matches by score in descending order
    all_matches.sort(key=lambda x: x[1], reverse=True)

    # Find the first match with the required depth
    for match, score in all_matches:
        if len(match) >= min_depth:
            #  return match and score
            # print("Matched category:", match, "Score:", score)
            return [match, score]
            # return match

    # If no match meets the depth requirement, return "Unknown" placeholders
    return ["Unknown"] * min_depth


# Example usage:


# Load category tree from public-category.json
with open('public-category.json', 'r') as file:
    categories = json.load(file)[0]  # Assuming the first element is the category tree

# if __name__ == "__main__":
#
#     matched_category, score = find_best_category_fuzzy(sku_data, categories)
#     print(f"Fuzzy matched category: {matched_category}, Score: {score}")

# execute the script for debug
def test1():
    sku_data = {
        'primary_category': 'Clothing > Sweats & Hoodies',
        'name': 'Unisex Hoodie',
        'gender': 'Unisex',
        'description': '',
        'attribute_set': 'Unisex',
        'customer_segment': 'Fashion',
    }
    sku_data = {
        "primary_category": "Female/Shoes/Dress Shoes",
        "name": "Secret Garden Dress",
        "attribute_set": "female",
        "gender": "female"
    }
    sku_data = {
        "primary_category": "Female/Clothing/Swimwear",
        "name": "Amalfi Cross Front Multifit One Piece Black",
        "attribute_set": "Apparel",
        "gender": "female"
    }

    matched_category, score = find_best_matched_category(sku_data, categories)
    print("Matched Category:", " > ".join(matched_category))
    print("Score:", score)

    # matched_category = find_best_matched_category(primary_category, category_tree)
    # if matched_category:
    #     print("Matched Category:", " > ".join(matched_category))
    # else:
    #     print("No matching category found.")



# Matched category: Fashion > Footwear > Dress Shoes > Slip On Dress Shoes, Score: 54.20560747663551
# input_file = 'data/input_primary_category_6.csv'
# output_file = 'data/output_matched_category.csv'

# read from input csv
if __name__ == "__main__":
    # test1()
    # exit()
    input_file = input("Enter the input file: ")
    input_file = 'data/' + input_file
    output_file = 'data/' + 'output_matched_' + input_file.split('/')[-1]

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = ['sku', 'primary_category', 'attribute_set', 'customer_segment', 'matched_category', 'matched_score',
                      'current_item_category_group', 'name',
                      'description'];
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            sku_data = {key: value for key, value in row.items()}

            # matched_category, score = find_best_category_fuzzy(sku_data, categories)
            matched_category, score = find_best_matched_category(sku_data, categories)

            # print(f"Fuzzy matched category: {matched_category}, Score: {score}")

            matched_category_str = " > ".join(matched_category) if matched_category else "No Match Found"
            # print("Matched Category:", matched_category_str);

            # writer.writerow({field: row.get(field, '') for field in fieldnames})
            rowsValues = {field: row.get(field, '') for field in fieldnames}
            writer.writerow({
                **rowsValues,  # Include all input data
                'matched_category': matched_category_str,
                'matched_score': score
            })
