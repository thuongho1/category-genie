# import csv
# import json
# import re
# from collections import defaultdict
#
# from fuzzywuzzy import fuzz
#
#
# # Function to dynamically generate type_mapping
# def generate_type_mapping(file_path):
#     type_mapping = defaultdict(set)
#
#     # Load the dataset
#     with open(file_path, 'r') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             # Extract product type from primary_category
#             primary_category = row['primary_category']
#             product_type = primary_category.lower()  # Use the full path as the product type
#             # Extract related terms from name, description, and matched_category
#             # related_text = f"{row['primary_category'] row['name']}".lower()
#             related_text = f" {row['primary_category']}".lower()
#
#             related_terms = re.findall(r'\b\w+\b', related_text)  # Extract words
#             # type_mapping[product_type].add(primary_category.lower())  # Add full path
#
#             # Add terms to the type mapping
#             type_mapping[product_type].update(related_terms)
#
#     # Convert sets to lists for JSON compatibility
#     return {key: list(terms) for key, terms in type_mapping.items()}
#
#
# def find_best_matched_category(category_tree, primary_category, name=None, gender=None, description=None, extra_input=None, type_mapping=None,
#                                min_depth=3):
#     def traverse_tree(tree, path):
#         matches = []
#
#         for category in tree:
#             current_path = path + [category["label"]]
#             # Combine factors for comparison
#             combined_input = f"{primary_category} {name or ''} {gender or ''} {description or ''} {extra_input or ''}".lower()
#             combined_category = " > ".join(current_path).lower()
#
#             # Calculate similarity score
#             score = fuzz.token_set_ratio(combined_input, combined_category)
#             # Boost score for exact keyword matches
#             # keywords = primary_category.lower().split("##")[-1].split()
#             # for keyword in keywords:
#             #     if keyword in combined_category:
#             #         score += 15  # Boost for matching keywords
#
#             # Penalize "Kids" category if age group is not "Kids" and "kids" is not in name/description
#             if "kids" in combined_category and (
#                     extra_input != "Kids" and "kids" not in (name or "").lower() and "kids" not in (description or "").lower()):
#                 score -= 20
#             # Get related terms for the primary category
#
#             # Get related terms for the input primary_category
#             related_terms = type_mapping.get(primary_category.lower(), []) if type_mapping else []
#             # print("Matching terms:", related_terms)
#
#             # Calculate relevance score based on related terms
#             if related_terms:
#                 matching_terms = [term for term in related_terms if term in combined_category]
#                 relevance_score = len(matching_terms) / len(related_terms) * 20  # Adjust weight as needed
#                 score += relevance_score
#
#                 # Penalize if no related terms match
#                 if not matching_terms:
#                     score -= 20  # Adjust penalty value as needed
#
#             # Boost score if gender matches
#             # if gender and gender.lower() in combined_category:
#             #     score += 10  # Adjust the boost value as needed
#             # Penalize "Kids" category if age group is not "Kids" and "kids" is not in name/description
#             # if "kids" in combined_category and (
#             #         extra_input != "Kids" and "kids" not in (name or "").lower() and "kids" not in (description or "").lower()):
#             #     score -= 20  # Penalize "Kids" category
#
#             matches.append((current_path, score))
#
#             # Recursively check children
#             if "children" in category:
#                 matches.extend(traverse_tree(category["children"], current_path))
#
#         return matches
#
#     # Get all matches with scores
#     all_matches = traverse_tree(category_tree, [])
#
#     # Sort matches by score in descending order
#     all_matches.sort(key=lambda x: x[1], reverse=True)
#     # print
#     # print("All matches with scores:", all_matches)
#
#     # Find the first match with the required depth
#     for match, score in all_matches:
#         if len(match) >= min_depth:
#             #  return match and score
#             # print("Matched category:", match, "Score:", score)
#             return [match, score]
#             # return match
#
#     # If no match meets the depth requirement, return "Unknown" placeholders
#     return ["Unknown"] * min_depth
#
#
# # -----------------
#
# # Load category tree from public-category.json
# with open('public-category.json', 'r') as file:
#     category_tree = json.load(file)[0]  # Assuming the first element is the category tree
#
# # Read input CSV and write results to output CSV
# # input_file = 'data/input_primary_category.csv'
# input_file = 'data/input_primary_category_3.csv'
# # output_file = 'data/output_matched_category.csv'
# output_file = 'data/' + 'output_matched_' + input_file.split('/')[-1]
#
# # read from input csv
# if __name__ == "__main__":
#     # // read primary_category from input csv
#     # input_file = input("Enter the input_file (or type 'exit' to quit): ")
#     type_mapping = generate_type_mapping(input_file)
#     #  save type_mapping to json file
#     with open('data/type_mapping.json', 'w') as json_file:
#         json.dump(type_mapping, json_file, indent=2)
#
#     with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
#         reader = csv.DictReader(infile)
#         # sku, primary_category, name, attribute_set, gender, description, department, customer_segment
#         fieldnames = ['sku', 'primary_category', 'attribute_set','customer_segment','matched_category', 'matched_score', 'name',  'gender', 'description', 'department',
#
#                       ]
#         writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#         writer.writeheader()
#
#         for row in reader:
#             primary_category = row['primary_category']
#             name = row.get('name', None)
#             gender = row.get('gender', None)
#             description = row.get('description', None)
#             attribute_set = row.get('attribute_set', None)
#             department = row.get('department', None)
#             customer_segment = row.get('customer_segment', None)
#             # print("Primary Category:", primary_category)
#
#             sku = row['sku']
#
#             #  combined_input = all the data from input csv except matched_category, sku
#             combined_extra_input = " ".join(
#                 [f"{value}" for key, value in row.items() if key not in ['matched_category', 'sku', 'primary_category', 'name', 'gender']])
#             # print("Combined Extra Input:", combined_extra_input)
#             # find_best_matched_category [match, score]
#             matched_category, score = find_best_matched_category(category_tree, primary_category, name, gender, '', combined_extra_input, type_mapping)
#
#             matched_category_str = " > ".join(matched_category) if matched_category else "No Match Found"
#             # print("Matched Category:", matched_category_str);
#
#             writer.writerow({
#                 'sku': sku,
#                 'primary_category': primary_category,
#                 'attribute_set': attribute_set,
#                 'customer_segment': customer_segment,
#                 'matched_category': matched_category_str,
#                 'matched_score': score,
#                 'name': name,
#                 'gender': gender,
#                 'description': description,
#                 'department': department,
#             })
#
#     # while True:
#     # #     Shoes » Sneakers » Low-Tops
#     #     primary_category = input("Enter the primary category (or type 'exit' to quit): ")
#     #     if primary_category.lower() == 'exit':
#     #         print("Exiting the program.")
#     #         break
#     # # primary_category = "Clothing > Sports Bras & Crops"
#     # # // get primary_category from input
#     # #     primary_category = input("Enter the primary category: ")
#     #
#     #
#     #     matched_category = find_best_matched_category(primary_category, category_tree)
#     #     if matched_category:
#     #         print("Matched Category:", " > ".join(matched_category))
#     #     else:
#     #         print("No matching category found.")
#
#
# # execute the script for debug
# def test1():
#     # while True:
#     #     primary_category = input("Enter the primary category (or type 'exit' to quit): ")
#     #     if primary_category.lower() == 'exit':
#     #         print("Exiting the program.")
#     #         break
#     # Accessories##Socks##Ankle Socks,Kids > Accessories > Socks > Ankle,Puma Evoknit Crop Top Womens,Female,
#     primary_category = "Clothing##Sweats & Hoodies"
#     name = "Unisex Hoodie"
#     gender = "Unisex"
#     description = "Comfortable and stylish hoodie for all genders"
#     extra_input = None
#     matched_category = find_best_matched_category(primary_category, category_tree, name, gender, description, extra_input)
#     print("Matched Category:", " > ".join(matched_category))
#
#     # matched_category = find_best_matched_category(primary_category, category_tree)
#     # if matched_category:
#     #     print("Matched Category:", " > ".join(matched_category))
#     # else:
#     #     print("No matching category found.")
