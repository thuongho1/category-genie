import json
import re
from difflib import SequenceMatcher

def flatten_categories(categories, path=None):
    """Recursively flatten the category tree into a list of full paths."""
    if path is None:
        path = []
    flat = []
    for cat in categories:
        current_path = path + [cat['label']]
        if 'children' in cat and cat['children']:
            flat.extend(flatten_categories(cat['children'], current_path))
        else:
            flat.append(' > '.join(current_path))
    return flat

def clean_text(text):
    """Lowercase and remove non-alphanumeric characters for comparison."""
    return re.sub(r'[^a-z0-9 ]', '', text.lower())

def score_category(sku_data, category_path):
    """Score a category path based on similarity to SKU data."""
    # Combine relevant SKU fields
    sku_text = ' '.join([
        sku_data.get('primary_category', ''),
        sku_data.get('name', ''),
        sku_data.get('attribute_set', ''),
        sku_data.get('gender', '')
    ])
    sku_text = clean_text(sku_text)
    category_text = clean_text(category_path)
    # Use SequenceMatcher for fuzzy matching
    return SequenceMatcher(None, sku_text, category_text).ratio() * 100

def find_best_category(sku_data, categories):
    flat_categories = flatten_categories(categories)
    best_score = 0
    best_category = None
    for cat_path in flat_categories:
        score = score_category(sku_data, cat_path)
        if score > best_score:
            best_score = score
            best_category = cat_path
    return best_category, best_score

# Example usage:
# SE201AA50KNX,Female/Clothing/Swimwear,Amalfi Cross Front Multifit One Piece Black,Apparel,female,Amalfi Cross Front Multifit One Piece Black,Apparel,Fashion

sku_data = {
    "primary_category": "Female/Clothing/Swimwear",
    "name": "Amalfi Cross Front Multifit One Piece Black",
    "attribute_set": "Apparel",
    "gender": "female"
}

# Load category tree from public-category.json
with open('public-category.json', 'r') as file:
    categories = json.load(file)[0]  # Assuming the first element is the category tree

if __name__ == "__main__":

    # Example SKU data
    print("SKU Data:", sku_data)
    matched_category, score = find_best_category(sku_data, categories)
    print(f"Matched category: {matched_category}, Score: {score}")
