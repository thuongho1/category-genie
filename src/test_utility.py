import re


def clean_text(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower())


def build_combined_input(sku_data, weights=None):
    """Build a weighted, cleaned input string from SKU data."""
    if not weights:
        weights = {}

    primary_category = format_primary_category(sku_data.get('primary_category', ''))

    combined_input = ' '.join([
        primary_category * weights.get('primary_category', 1),
        clean_text(sku_data.get('attribute_set', '') * weights.get('attribute_set', 1)),
        clean_text(sku_data.get('customer_segment', '') * weights.get('customer_segment', 1)),
        clean_text(sku_data.get('name', '') * weights.get('name', 2)),
        # clean_text(sku_data.get('description', '') * weights.get('description', 1)),
    ])

    return combined_input


def format_primary_category(primary_category):
    """Format primary category string by removing unwanted characters."""
    primary_category = primary_category.replace('Root Category##', '')
    primary_category = primary_category.replace('##', ' ')
    primary_category = primary_category.replace('/', ' ')

    return primary_category.lower()
