"""Feature engineering for ingredient encoding into ML features."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# EU allergen list (26 mandatory allergens in cosmetics)
EU_ALLERGENS = {
    "limonene",
    "linalool",
    "citral",
    "coumarin",
    "eugenol",
    "geraniol",
    "farnesol",
    "fragrance",
    "parfum",
    "essential oil",
    "alcohol",
    "phenoxyethanol",
}

# Chemical families
CHEMICAL_FAMILIES = {
    "preservative": ["paraben", "phenoxyethanol", "sodium benzoate", "potassium sorbate"],
    "surfactant": ["sodium lauryl sulfate", "sodium laureth sulfate", "cetearyl"],
    "emollient": ["glycerin", "squalane", "jojoba", "argan", "coconut"],
    "fragrance": ["fragrance", "parfum", "essential oil", "limonene"],
    "colorant": ["ci ", "titanium dioxide", "iron oxide", "mica"],
    "thickener": ["xanthan gum", "carbomer", "cellulose"],
    "humectant": ["glycerin", "hyaluronic acid", "sorbitol"],
    "antioxidant": ["tocopherol", "ascorbic acid", "bht", "bha"],
    "chelating agent": ["edta", "citrates"],
    "exfoliant": ["salicylic acid", "glycolic acid", "lactic acid"],
}


class IngredientEncoder:
    """Encodes ingredient names into feature vectors for ML models."""

    def __init__(self, reference_db_path: Optional[Path] = None) -> None:
        """
        Initialize encoder with optional reference database.

        Args:
            reference_db_path: Path to parquet file with ingredient safety data
        """
        self.reference_db = self._load_reference_db(reference_db_path)

    def _load_reference_db(self, db_path: Optional[Path]) -> pd.DataFrame:
        """
        Load reference ingredient database.

        Args:
            db_path: Path to reference database parquet file

        Returns:
            DataFrame with columns: ingredient_name, ewg_score, hazard_level,
                                    allergen, comedogenic_rating, endocrine_disruptor,
                                    pregnancy_safe, vegan, chemical_family
        """
        if db_path and db_path.exists():
            try:
                df = pd.read_parquet(db_path)
                logger.info(f"Loaded reference DB with {len(df)} ingredients from {db_path}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load reference DB: {e}")

        # Return empty dataframe structure
        logger.info("Using empty reference database structure")
        return pd.DataFrame(
            columns=[
                "ingredient_name",
                "ewg_score",
                "hazard_level",
                "allergen",
                "comedogenic_rating",
                "endocrine_disruptor",
                "pregnancy_safe",
                "vegan",
                "chemical_family",
            ]
        )

    def encode_ingredient(self, name: str) -> Dict[str, any]:
        """
        Encode single ingredient into feature dictionary.

        Features:
        - ewg_score: 0-10 (EWG hazard score)
        - chemical_family: string (preservative, surfactant, etc)
        - allergen: bool (EU 26 allergens)
        - comedogenic_rating: 0-5 (pore-clogging potential)
        - endocrine_disruptor: bool
        - pregnancy_safe: bool
        - vegan: bool

        Args:
            name: Ingredient name (should be normalized first)

        Returns:
            Dictionary with all feature values
        """
        if not isinstance(name, str):
            return self._default_features()

        name_lower = name.lower().strip()

        # Try to find in reference DB
        if not self.reference_db.empty:
            matches = self.reference_db[
                self.reference_db["ingredient_name"].str.lower() == name_lower
            ]
            if not matches.empty:
                row = matches.iloc[0]
                return {
                    "ingredient_name": name,
                    "ewg_score": float(row.get("ewg_score", 5.0)),
                    "hazard_level": str(row.get("hazard_level", "UNKNOWN")),
                    "chemical_family": str(row.get("chemical_family", "unknown")),
                    "allergen": bool(row.get("allergen", False)),
                    "comedogenic_rating": float(row.get("comedogenic_rating", 2.0)),
                    "endocrine_disruptor": bool(row.get("endocrine_disruptor", False)),
                    "pregnancy_safe": bool(row.get("pregnancy_safe", True)),
                    "vegan": bool(row.get("vegan", True)),
                }

        # Fallback to heuristic scoring
        return self._encode_heuristic(name_lower)

    def encode_ingredient_list(self, names: List[str]) -> pd.DataFrame:
        """
        Encode list of ingredients into feature DataFrame.

        Args:
            names: List of ingredient names

        Returns:
            DataFrame where each row is an ingredient with features as columns
        """
        features = [self.encode_ingredient(name) for name in names]
        df = pd.DataFrame(features)
        logger.debug(f"Encoded {len(df)} ingredients into features")
        return df

    def _encode_heuristic(self, name_lower: str) -> Dict[str, any]:
        """
        Generate features using heuristic rules when reference DB unavailable.

        Args:
            name_lower: Lowercase ingredient name

        Returns:
            Feature dictionary
        """
        # Determine chemical family
        chemical_family = self._classify_chemical_family(name_lower)

        # Check if allergen
        is_allergen = any(allergen in name_lower for allergen in EU_ALLERGENS)

        # Default EWG score based on family
        family_ewg_defaults = {
            "preservative": 3.0,
            "surfactant": 4.0,
            "fragrance": 4.0,
            "colorant": 2.0,
            "emollient": 1.0,
            "unknown": 5.0,
        }
        ewg_score = family_ewg_defaults.get(chemical_family, 5.0)

        # Adjust for known problematic ingredients
        if any(x in name_lower for x in ["oxybenzone", "coal tar", "deet"]):
            ewg_score = 8.0
            hazard_level = "HAZARDOUS"
        elif any(x in name_lower for x in ["paraben", "phthalate", "formaldehyde"]):
            ewg_score = 6.0
            hazard_level = "MODERATE"
        elif any(x in name_lower for x in ["water", "glycerin", "oil"]):
            ewg_score = 1.0
            hazard_level = "SAFE"
        else:
            hazard_level = "MODERATE" if ewg_score > 5 else "SAFE"

        return {
            "ingredient_name": name_lower,
            "ewg_score": ewg_score,
            "hazard_level": hazard_level,
            "chemical_family": chemical_family,
            "allergen": is_allergen,
            "comedogenic_rating": 2.0,  # default middle value
            "endocrine_disruptor": ewg_score > 6,
            "pregnancy_safe": ewg_score < 7,
            "vegan": not any(x in name_lower for x in ["lanolin", "beeswax", "collagen"]),
        }

    @staticmethod
    def _classify_chemical_family(name_lower: str) -> str:
        """
        Classify ingredient into chemical family.

        Args:
            name_lower: Lowercase ingredient name

        Returns:
            Chemical family string
        """
        for family, keywords in CHEMICAL_FAMILIES.items():
            if any(keyword in name_lower for keyword in keywords):
                return family
        return "unknown"

    @staticmethod
    def _default_features() -> Dict[str, any]:
        """Return default feature values for invalid input."""
        return {
            "ingredient_name": "unknown",
            "ewg_score": 5.0,
            "hazard_level": "UNKNOWN",
            "chemical_family": "unknown",
            "allergen": False,
            "comedogenic_rating": 2.0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
        }


# Convenience functions
_default_encoder = IngredientEncoder()


def encode_ingredient(name: str) -> Dict[str, any]:
    """Encode single ingredient using default encoder."""
    return _default_encoder.encode_ingredient(name)


def encode_ingredient_list(names: List[str]) -> pd.DataFrame:
    """Encode ingredient list using default encoder."""
    return _default_encoder.encode_ingredient_list(names)
