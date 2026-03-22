"""Ingredient name normalization using INCI standards and synonym mapping."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd

logger = logging.getLogger(__name__)

# Default INCI synonym mappings (in-memory fallback)
DEFAULT_INCI_MAPPING = {
    "aqua": "water",
    "water": "water",
    "h2o": "water",
    "alcohol": "alcohol",
    "ethanol": "alcohol",
    "cetyl alcohol": "cetyl alcohol",
    "stearyl alcohol": "stearyl alcohol",
    "cetearyl alcohol": "cetearyl alcohol",
    "glycerin": "glycerin",
    "glycerol": "glycerin",
    "propylene glycol": "propylene glycol",
    "butylene glycol": "butylene glycol",
    "xanthan gum": "xanthan gum",
    "citric acid": "citric acid",
    "sodium citrate": "sodium citrate",
    "sodium hydroxide": "sodium hydroxide",
    "potassium hydroxide": "potassium hydroxide",
    "sodium chloride": "sodium chloride",
    "salt": "sodium chloride",
    "fragrance": "fragrance",
    "parfum": "fragrance",
    "essential oil": "fragrance",
    "methylparaben": "methylparaben",
    "ethylparaben": "ethylparaben",
    "propylparaben": "propylparaben",
    "butylparaben": "butylparaben",
    "parabens": "methylparaben",
    "phenoxyethanol": "phenoxyethanol",
    "edta": "edta",
    "disodium edta": "edta",
    "tetrasodium edta": "edta",
    "titanium dioxide": "titanium dioxide",
    "ci 77891": "titanium dioxide",
    "iron oxides": "iron oxides",
    "ci 77492": "iron oxide yellow",
    "ci 77491": "iron oxide red",
    "ci 77499": "iron oxide black",
    "mica": "mica",
    "talc": "talc",
    "kaolin": "kaolin",
    "zinc oxide": "zinc oxide",
    "colloidal silver": "colloidal silver",
    "nanoparticles": "nanoparticles",
    "oxybenzone": "oxybenzone",
    "avobenzone": "avobenzone",
    "octinoxate": "octinoxate",
    "retinol": "retinol",
    "retinyl palmitate": "retinol derivative",
    "retinaldehyde": "retinol derivative",
    "sodium benzoate": "sodium benzoate",
    "potassium sorbate": "potassium sorbate",
    "calcium pantothenate": "panthenol",
    "panthenol": "panthenol",
    "niacinamide": "niacinamide",
    "vitamin e": "tocopherol",
    "tocopherol": "tocopherol",
    "tocopheryl acetate": "tocopherol",
    "vitamin c": "ascorbic acid",
    "ascorbic acid": "ascorbic acid",
    "hyaluronic acid": "hyaluronic acid",
    "salicylic acid": "salicylic acid",
    "glycolic acid": "glycolic acid",
    "lactic acid": "lactic acid",
    "azelaic acid": "azelaic acid",
    "kojic acid": "kojic acid",
    "alpha hydroxy acid": "hydroxy acid",
    "aha": "hydroxy acid",
    "bha": "salicylic acid",
    "beta hydroxy acid": "salicylic acid",
    "cetyl acetate": "cetyl acetate",
    "dimethicone": "dimethicone",
    "cyclomethicone": "cyclomethicone",
    "squalane": "squalane",
    "squalene": "squalene",
    "jojoba oil": "jojoba oil",
    "argan oil": "argan oil",
    "coconut oil": "coconut oil",
    "almond oil": "almond oil",
    "rosehip oil": "rosehip oil",
    "vitamin a": "retinol",
    "sodium sulfate": "sodium sulfate",
    "magnesium sulfate": "magnesium sulfate",
    "zinc pyrithione": "zinc pyrithione",
    "coal tar": "coal tar",
    "salicylic acid": "salicylic acid",
    "sulfur": "sulfur",
    "benzoyl peroxide": "benzoyl peroxide",
}


class IngredientNormaliser:
    """Normalizes ingredient names to INCI standards."""

    def __init__(self, inci_mapping_path: Optional[Path] = None) -> None:
        """
        Initialize normaliser with optional INCI mapping file.

        Args:
            inci_mapping_path: Path to parquet file with INCI synonym data.
                              If None, uses default in-memory mapping.
        """
        self.inci_map = self._load_inci_mapping(inci_mapping_path)

    def _load_inci_mapping(self, mapping_path: Optional[Path]) -> Dict[str, str]:
        """
        Load INCI mapping from file or use default.

        Args:
            mapping_path: Path to parquet file

        Returns:
            Dictionary of ingredient_name -> inci_name
        """
        if mapping_path and mapping_path.exists():
            try:
                df = pd.read_parquet(mapping_path)
                mapping = dict(zip(df["synonym"], df["inci_name"]))
                logger.info(f"Loaded {len(mapping)} INCI mappings from {mapping_path}")
                return mapping
            except Exception as e:
                logger.warning(f"Failed to load INCI mapping from {mapping_path}: {e}")

        logger.info("Using default INCI mapping")
        return DEFAULT_INCI_MAPPING

    def normalise_ingredient_name(self, name: str) -> str:
        """
        Normalize single ingredient name to INCI standard.

        Handles:
        - Color codes (CI XXXXX format)
        - Case-insensitive lookup
        - Whitespace normalization
        - Special chemical notation

        Args:
            name: Raw ingredient name

        Returns:
            Normalized INCI-compliant name

        Example:
            "AQUA" -> "water"
            "CI 77891" -> "titanium dioxide"
        """
        if not isinstance(name, str):
            return ""

        # Normalize whitespace and case
        name = name.strip().lower()

        if not name:
            return ""

        # Handle color code CI format: "CI 77891" -> look up "ci 77891"
        if name.startswith("ci "):
            normalized = self.inci_map.get(name, name)
            if normalized != name:
                logger.debug(f"Color code normalized: {name} -> {normalized}")
            return normalized

        # Check direct mapping
        if name in self.inci_map:
            return self.inci_map[name]

        # Try removing common suffices and affixes
        variations = [
            name,
            re.sub(r"\s+\(.*?\)", "", name),  # remove parenthetical info
            re.sub(r"\s*\(.*?\)", "", name),  # remove parenthetical
            name.replace("  ", " "),  # clean double spaces
        ]

        for variation in variations:
            if variation in self.inci_map:
                logger.debug(f"Ingredient normalized: {name} -> {self.inci_map[variation]}")
                return self.inci_map[variation]

        # Return as-is if no match found
        logger.debug(f"No INCI mapping found for: {name}")
        return name

    def normalise_ingredient_list(self, raw_text: str) -> List[str]:
        """
        Parse and normalize raw ingredient string into list of normalized names.

        Handles:
        - Comma-separated lists
        - Nested parentheses (e.g., "Aqua (Water), Glycerin (20%)")
        - Percentage values
        - Asterisks and symbols

        Args:
            raw_text: Raw ingredient text string (comma-separated)

        Returns:
            List of normalized ingredient names

        Example:
            "Aqua*, Glycerin (20%), CI 77891, Fragrance"
            -> ["water", "glycerin", "titanium dioxide", "fragrance"]
        """
        if not isinstance(raw_text, str) or not raw_text.strip():
            return []

        # Split by comma, handling nested parentheses
        ingredients = self._split_ingredients(raw_text)

        # Normalize each ingredient
        normalized = []
        for ingredient in ingredients:
            # Remove percentage and parenthetical info
            cleaned = re.sub(r"\s*\(.*?\)", "", ingredient)  # remove parentheses
            cleaned = re.sub(r"[\d%\*]+", "", cleaned)  # remove numbers, %, *
            cleaned = cleaned.strip()

            if cleaned:
                normalized_name = self.normalise_ingredient_name(cleaned)
                if normalized_name not in normalized:  # avoid duplicates
                    normalized.append(normalized_name)

        logger.info(f"Normalized {len(normalized)} ingredients from raw text")
        return normalized

    @staticmethod
    def _split_ingredients(text: str) -> List[str]:
        """
        Split ingredient string by commas, respecting parentheses.

        Args:
            text: Comma-separated ingredient string

        Returns:
            List of ingredient strings

        Example:
            "Aqua, Glycerin (20%), sodium hydroxide, water (and) salt"
            -> ["Aqua", "Glycerin (20%)", "sodium hydroxide", "water", "salt"]
        """
        ingredients = []
        current = ""
        depth = 0

        for char in text:
            if char == "(":
                depth += 1
                current += char
            elif char == ")":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                if current.strip():
                    ingredients.append(current.strip())
                current = ""
            else:
                current += char

        if current.strip():
            ingredients.append(current.strip())

        return ingredients


# Convenience functions for direct usage
_default_normaliser = IngredientNormaliser()


def normalise_ingredient_name(name: str) -> str:
    """Normalize a single ingredient name using default normaliser."""
    return _default_normaliser.normalise_ingredient_name(name)


def normalise_ingredient_list(raw_text: str) -> List[str]:
    """Normalize an ingredient list using default normaliser."""
    return _default_normaliser.normalise_ingredient_list(raw_text)
