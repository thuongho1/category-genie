# Category Matching Tool

This project is designed to match primary categories from an input file to a predefined category tree (`public-category.json`). It supports fuzzy matching, semantic matching, and overrides for specific SKUs.

## Features
- **Fuzzy Matching**: Matches categories based on string similarity.
- **Semantic Matching**: Uses pre-trained embeddings for more accurate matching.
- **Override Support**: Allows manual overrides for specific SKUs.
- **Customizable Depth**: Configurable minimum depth for category matching.

## Prerequisites
1. Python 3.x installed on your system.
2. Required Python libraries installed (see below).

## Setup
1. Create a `data` folder in the project root.
2. Create an `output` folder in the project root.
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
    ```
   


Running the Tool
Run the following command to execute the script:
/usr/bin/python3 src/main.py

Command-Line Prompts
Input File: Enter the name of the input file (default: input_primary_category_verify.csv).
Override File: Enter the name of the override file (default: override_primary_category_6.csv).
Output Filename Suffix: Enter a suffix for the output file (optional).


Output
The output file will be saved in the output folder with a timestamped filename. It includes the following fields:  
SKU
Primary Category
Fuzzy Matched Category and Score
Semantic Matched Category and Score
Other relevant fields from the input file.
