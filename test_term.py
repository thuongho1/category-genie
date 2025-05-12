import csv
from collections import defaultdict
import re

def generate_type_mapping(file_path):
    type_mapping = defaultdict(set)

    # Load the dataset
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract product type from primary_category
            primary_category = row['primary_category']
            product_type = primary_category.split('/')[-1].lower()

            # Extract related terms from name, description, and matched_category
            related_text = f" {row['matched_category']}".lower()
            related_terms = re.findall(r'\b\w+\b', related_text)  # Extract words

            # Add terms to the type mapping
            type_mapping[product_type].update(related_terms)

    # Convert sets to lists for JSON compatibility
    return {key: list(terms) for key, terms in type_mapping.items()}

# Example usage
file_path = 'data/output_matched_category.csv'
type_mapping = generate_type_mapping(file_path)

# Print or save the type mapping
import json


if __name__ == "__main__":
    print(json.dumps(type_mapping, indent=2))