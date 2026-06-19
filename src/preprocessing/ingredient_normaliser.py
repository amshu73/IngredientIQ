"""Ingredient name normalization using INCI standards and synonym mapping."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd

logger = logging.getLogger(__name__)

# Default INCI synonym mappings (in-memory fallback) - EXPANDED
DEFAULT_INCI_MAPPING = {
    # Water and solvents
    "aqua": "water",
    "water": "water",
    "h2o": "water",
    "eau": "water",
    "alcohol": "alcohol",
    "ethanol": "alcohol",
    "ethyl alcohol": "alcohol",
    "sd alcohol": "alcohol",
    "denat. alcohol": "alcohol",
    
    # Alcohols (fatty)
    "cetyl alcohol": "cetyl alcohol",
    "stearyl alcohol": "stearyl alcohol",
    "cetearyl alcohol": "cetearyl alcohol",
    "cetostearyl alcohol": "cetearyl alcohol",
    "behenyl alcohol": "behenyl alcohol",
    
    # Glycerin and glycols
    "glycerin": "glycerin",
    "glycerol": "glycerin",
    "glycerine": "glycerin",
    "propylene glycol": "propylene glycol",
    "butylene glycol": "butylene glycol",
    "caprylyl glycol": "caprylyl glycol",
    "pentylene glycol": "pentylene glycol",
    
    # Gums and thickeners
    "xanthan gum": "xanthan gum",
    "guar gum": "guar gum",
    "locust bean gum": "locust bean gum",
    "carbomer": "carbomer",
    "hydroxyethylcellulose": "hydroxyethylcellulose",
    "cellulose": "cellulose",
    "carrageenan": "carrageenan",
    
    # Acids
    "citric acid": "citric acid",
    "sodium citrate": "sodium citrate",
    "lactic acid": "lactic acid",
    "glycolic acid": "glycolic acid",
    "salicylic acid": "salicylic acid",
    "hyaluronic acid": "hyaluronic acid",
    "sodium hyaluronate": "hyaluronic acid",
    "ascorbic acid": "ascorbic acid",
    "vitamin c": "ascorbic acid",
    "l-ascorbic acid": "ascorbic acid",
    
    # Bases
    "sodium hydroxide": "sodium hydroxide",
    "potassium hydroxide": "potassium hydroxide",
    "triethanolamine": "triethanolamine",
    "tea": "triethanolamine",
    "aminomethyl propanol": "aminomethyl propanol",
    
    # Salts
    "sodium chloride": "sodium chloride",
    "salt": "sodium chloride",
    "sea salt": "sodium chloride",
    "magnesium sulfate": "magnesium sulfate",
    "epsom salt": "magnesium sulfate",
    
    # Fragrance
    "fragrance": "fragrance",
    "parfum": "fragrance",
    "perfume": "fragrance",
    "essential oil": "fragrance",
    "aroma": "fragrance",
    
    # Parabens
    "methylparaben": "methylparaben",
    "ethylparaben": "ethylparaben",
    "propylparaben": "propylparaben",
    "butylparaben": "butylparaben",
    "parabens": "methylparaben",
    
    # Other preservatives
    "phenoxyethanol": "phenoxyethanol",
    "sodium benzoate": "sodium benzoate",
    "potassium sorbate": "potassium sorbate",
    "benzyl alcohol": "benzyl alcohol",
    "methylisothiazolinone": "methylisothiazolinone",
    "methylchloroisothiazolinone": "methylchloroisothiazolinone",
    
    # EDTA
    "edta": "edta",
    "disodium edta": "edta",
    "tetrasodium edta": "edta",
    "edetate disodium": "edta",
    
    # Minerals and pigments
    "titanium dioxide": "titanium dioxide",
    "ci 77891": "titanium dioxide",
    "zinc oxide": "zinc oxide",
    "ci 77947": "zinc oxide",
    "iron oxides": "iron oxides",
    "ci 77492": "iron oxide yellow",
    "ci 77491": "iron oxide red",
    "ci 77499": "iron oxide black",
    "mica": "mica",
    "ci 77019": "mica",
    "talc": "talc",
    "kaolin": "kaolin",
    "china clay": "kaolin",
    "bentonite": "bentonite",
    
    # UV filters
    "oxybenzone": "oxybenzone",
    "benzophenone-3": "oxybenzone",
    "avobenzone": "avobenzone",
    "butyl methoxydibenzoylmethane": "avobenzone",
    "octinoxate": "octinoxate",
    "ethylhexyl methoxycinnamate": "octinoxate",
    "octocrylene": "octocrylene",
    "homosalate": "homosalate",
    "octisalate": "octisalate",
    
    # Retinoids
    "retinol": "retinol",
    "vitamin a": "retinol",
    "retinyl palmitate": "retinol derivative",
    "retinaldehyde": "retinol derivative",
    "retinoic acid": "retinoic acid",
    "tretinoin": "retinoic acid",
    
    # Vitamins
    "panthenol": "panthenol",
    "pro-vitamin b5": "panthenol",
    "d-panthenol": "panthenol",
    "calcium pantothenate": "panthenol",
    "niacinamide": "niacinamide",
    "nicotinamide": "niacinamide",
    "vitamin b3": "niacinamide",
    "vitamin e": "tocopherol",
    "tocopherol": "tocopherol",
    "tocopheryl acetate": "tocopherol",
    "dl-alpha tocopherol": "tocopherol",
    "biotin": "biotin",
    "vitamin b7": "biotin",
    
    # Oils and butters
    "jojoba oil": "jojoba oil",
    "simmondsia chinensis": "jojoba oil",
    "argan oil": "argan oil",
    "argania spinosa": "argan oil",
    "coconut oil": "coconut oil",
    "cocos nucifera": "coconut oil",
    "almond oil": "almond oil",
    "prunus amygdalus dulcis": "almond oil",
    "rosehip oil": "rosehip oil",
    "rosa canina": "rosehip oil",
    "shea butter": "shea butter",
    "butyrospermum parkii": "shea butter",
    "cocoa butter": "cocoa butter",
    "theobroma cacao": "cocoa butter",
    "olive oil": "olive oil",
    "olea europaea": "olive oil",
    "sunflower oil": "sunflower oil",
    "helianthus annuus": "sunflower oil",
    
    # Silicones
    "dimethicone": "dimethicone",
    "cyclomethicone": "cyclomethicone",
    "cyclopentasiloxane": "cyclopentasiloxane",
    "dimethiconol": "dimethiconol",
    "phenyl trimethicone": "phenyl trimethicone",
    
    # Emollients
    "squalane": "squalane",
    "squalene": "squalene",
    "caprylic/capric triglyceride": "caprylic triglyceride",
    "coco-caprylate": "coco-caprylate",
    "isopropyl myristate": "isopropyl myristate",
    "isopropyl palmitate": "isopropyl palmitate",
    
    # Surfactants
    "sodium lauryl sulfate": "sodium lauryl sulfate",
    "sls": "sodium lauryl sulfate",
    "sodium laureth sulfate": "sodium laureth sulfate",
    "sles": "sodium laureth sulfate",
    "cocamidopropyl betaine": "cocamidopropyl betaine",
    "coco-glucoside": "coco-glucoside",
    "decyl glucoside": "decyl glucoside",
    "sodium cocoyl isethionate": "sodium cocoyl isethionate",
    
    # Actives
    "alpha hydroxy acid": "hydroxy acid",
    "aha": "hydroxy acid",
    "bha": "salicylic acid",
    "beta hydroxy acid": "salicylic acid",
    "azelaic acid": "azelaic acid",
    "kojic acid": "kojic acid",
    "tranexamic acid": "tranexamic acid",
    "mandelic acid": "mandelic acid",
    
    # Plant extracts
    "aloe vera": "aloe vera",
    "aloe barbadensis": "aloe vera",
    "green tea extract": "green tea extract",
    "camellia sinensis": "green tea extract",
    "chamomile": "chamomile",
    "chamomilla recutita": "chamomile",
    "calendula": "calendula",
    "calendula officinalis": "calendula",
    
    # Peptides and proteins
    "peptide": "peptide",
    "palmitoyl pentapeptide": "peptide",
    "acetyl hexapeptide": "peptide",
    "collagen": "collagen",
    "hydrolyzed collagen": "collagen",
    "keratin": "keratin",
    "hydrolyzed keratin": "keratin",
    
    # Others
    "ceramide": "ceramide",
    "niacinamide": "niacinamide",
    "allantoin": "allantoin",
    "bisabolol": "bisabolol",
    "caffeine": "caffeine",
    "urea": "urea",
    "sodium pca": "sodium pca",
    "petrolatum": "petrolatum",
    "petroleum jelly": "petrolatum",
    "vaseline": "petrolatum",
    "mineral oil": "mineral oil",
    "paraffinum liquidum": "mineral oil",
    
    # Problematic
    "coal tar": "coal tar",
    "sulfur": "sulfur",
    "benzoyl peroxide": "benzoyl peroxide",
    "zinc pyrithione": "zinc pyrithione",
    "triclosan": "triclosan",
    "triclocarban": "triclocarban",
    "formaldehyde": "formaldehyde",
    "dmdm hydantoin": "dmdm hydantoin",
    "quaternium-15": "quaternium-15",
    "hydroquinone": "hydroquinone",
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
