"""Feature engineering modules for ingredient encoding."""

from src.features.ingredient_encoder import (
    IngredientEncoder,
    encode_ingredient,
    encode_ingredient_list,
)

__all__ = [
    "IngredientEncoder",
    "encode_ingredient",
    "encode_ingredient_list",
]
