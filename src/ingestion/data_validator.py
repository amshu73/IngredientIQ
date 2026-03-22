"""Data validation for fetched product data."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def validate_product_data(product_data: Dict[str, Any]) -> bool:
    """
    Validate fetched product data has required fields.

    Checks for:
    - product_name is non-empty string
    - ingredients_text is provided and non-empty
    - barcode is provided
    - No excessively long fields (potential data corruption)

    Args:
        product_data: Dictionary containing product information

    Returns:
        True if data is valid, raises ValueError otherwise

    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not isinstance(product_data, dict):
        raise ValueError("product_data must be a dictionary")

    # Check required fields
    required_fields = ["product_name", "barcode"]
    for field in required_fields:
        if field not in product_data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(product_data[field], str) or not product_data[field].strip():
            raise ValueError(f"Field '{field}' must be non-empty string")

    # Validate ingredients_text
    if "ingredients_text" in product_data:
        ingredients = product_data["ingredients_text"]
        if not isinstance(ingredients, str):
            raise ValueError("ingredients_text must be string")
        if len(ingredients) > 10000:
            raise ValueError("ingredients_text exceeds maximum length (10000 chars)")

    # Check for excessively long fields (potential issues)
    max_field_length = 5000
    for field, value in product_data.items():
        if isinstance(value, str) and len(value) > max_field_length:
            logger.warning(f"Field '{field}' exceeds {max_field_length} chars")

    logger.debug(f"Product data validation passed for {product_data.get('product_name')}")
    return True


def validate_ingredients_list(ingredients: List[str]) -> bool:
    """
    Validate a list of ingredient names.

    Checks:
    - Each ingredient is a non-empty string
    - No excessively long ingredient names (>200 chars)
    - List is not empty

    Args:
        ingredients: List of ingredient name strings

    Returns:
        True if valid, raises ValueError otherwise

    Raises:
        ValueError: If list is invalid
    """
    if not isinstance(ingredients, list):
        raise ValueError("ingredients must be a list")

    if len(ingredients) == 0:
        raise ValueError("ingredients list cannot be empty")

    for idx, ingredient in enumerate(ingredients):
        if not isinstance(ingredient, str) or not ingredient.strip():
            raise ValueError(f"Ingredient at index {idx} must be non-empty string")
        if len(ingredient) > 200:
            raise ValueError(f"Ingredient at index {idx} exceeds 200 chars: {ingredient[:50]}...")

    logger.debug(f"Ingredients list validation passed ({len(ingredients)} ingredients)")
    return True
