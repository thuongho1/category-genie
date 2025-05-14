import json

def clean_text(text):
    """Utility function to clean and normalize text."""
    return ' '.join(text.lower().strip().split())

def traverse_tree(tree, path, input_keywords):
    """Recursively traverse the category tree to find the best match."""
    matches = []
    for category in tree:
        current_path = path + [category["label"]]
        combined_category = clean_text(" > ".join(current_path))

        # Calculate exact match score
        exact_match_score = sum(1 for keyword in input_keywords if keyword in combined_category)

        # Add level-based weighting
        level_weight = len(current_path) * 10
        total_score = exact_match_score * 20 + level_weight

        # Add the match to the list
        matches.append((current_path, total_score))

        # Recursively check children
        if "children" in category:
            matches.extend(traverse_tree(category["children"], current_path, input_keywords))
    return matches

def find_best_matched_category(input_data, category_tree):
    """Find the best-matched category from the tree."""
    input_keywords = clean_text(input_data).split("##")
    all_matches = traverse_tree(category_tree, [], input_keywords)
    all_matches.sort(key=lambda x: x[1], reverse=True)  # Sort by score in descending order
    best_match = all_matches[0] if all_matches else (["Unknown"], 0)
    return best_match

if __name__ == "__main__":
    # Example input data
    input_data = "Apparel Clothing##Sweats & Hoodies##Hoodies Clothing##Sweats & Hoodies##Hoodies Essential Logo Hoodie - Kids"

    # Load category tree from `public-category.json`
    with open('public-category.json', 'r') as file:
        category_tree = json.load(file)[0]  # Assuming the first element is the category tree

    # Find the best-matched category
    matched_category, score = find_best_matched_category(input_data, category_tree)
    print(f"Matched Category: {' > '.join(matched_category)}, Score: {score}")