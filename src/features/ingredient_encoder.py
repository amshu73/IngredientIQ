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

# Chemical families - expanded for better coverage
CHEMICAL_FAMILIES = {
    "preservative": [
        "paraben", "phenoxyethanol", "sodium benzoate", "potassium sorbate",
        "benzyl", "sorbic acid", "benzoic acid", "dehydroacetic acid"
    ],
    "surfactant": [
        "sodium lauryl sulfate", "sodium laureth sulfate", "cetearyl",
        "coco-glucoside", "decyl glucoside", "laureth", "lauryl",
        "cocamidopropyl betaine", "sodium cocoyl", "disodium cocoamphodiacetate"
    ],
    "emollient": [
        "glycerin", "squalane", "jojoba", "argan", "coconut",
        "shea butter", "cocoa butter", "cetyl alcohol", "stearyl alcohol",
        "caprylic", "capric", "dimethicone", "isopropyl", "mineral oil"
    ],
    "fragrance": [
        "fragrance", "parfum", "essential oil", "limonene", "linalool",
        "citronellol", "geraniol", "eugenol", "coumarin"
    ],
    "colorant": [
        "ci ", "titanium dioxide", "iron oxide", "mica", "carmine",
        "ultramarine", "chromium", "pigment"
    ],
    "thickener": [
        "xanthan gum", "carbomer", "cellulose", "acrylate", "hydroxyethyl",
        "guar gum", "locust bean", "carrageenan", "agar"
    ],
    "humectant": [
        "glycerin", "hyaluronic acid", "sorbitol", "propylene glycol",
        "butylene glycol", "panthenol", "urea", "honey"
    ],
    "antioxidant": [
        "tocopherol", "ascorbic acid", "bht", "bha", "vitamin e",
        "vitamin c", "green tea", "resveratrol", "ferulic acid"
    ],
    "chelating agent": [
        "edta", "citrates", "phytic acid", "gluconic acid"
    ],
    "exfoliant": [
        "salicylic acid", "glycolic acid", "lactic acid", "malic acid",
        "mandelic acid", "citric acid", "tartaric acid", "pha", "aha", "bha"
    ],
    "uv filter": [
        "oxybenzone", "avobenzone", "octinoxate", "octocrylene",
        "zinc oxide", "titanium dioxide", "mexoryl", "tinosorb"
    ],
    "solvent": [
        "water", "aqua", "alcohol", "ethanol", "propanol", "acetone"
    ],
    "vitamin": [
        "retinol", "niacinamide", "tocopherol", "ascorbic", "panthenol",
        "biotin", "pyridoxine", "thiamine"
    ],
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
                    "safety_label": str(row.get("safety_label", "UNKNOWN")),
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
        Enhanced with extensive pattern matching for common cosmetic ingredients.

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
            "humectant": 1.0,
            "antioxidant": 1.0,
            "thickener": 1.0,
            "unknown": 5.0,
        }
        ewg_score = family_ewg_defaults.get(chemical_family, 5.0)

        # HAZARDOUS ingredients (EWG 8-10)
        if any(x in name_lower for x in [
            "oxybenzone", "coal tar", "deet", "triclosan", "triclocarban",
            "formaldehyde", "quaternium-15", "dmdm hydantoin",
            "lead", "mercury", "hydroquinone", "benzene", "toluene"
        ]):
            ewg_score = 8.0
            safety_label = "HAZARDOUS"
        
        # MODERATE to HIGH concern (EWG 5-7)
        elif any(x in name_lower for x in [
            "paraben", "phthalate", "bha", "bht", "petrolatum",
            "mineral oil", "polyethylene", "propylene glycol",
            "sodium lauryl sulfate", "sodium laureth sulfate",
            "dea", "tea", "mea", "diethanolamine", "triethanolamine",
            "siloxane", "cyclotetrasiloxane", "cyclopentasiloxane"
        ]):
            ewg_score = 6.0
            safety_label = "MODERATE"
        
        # SAFE ingredients (EWG 1-2) - expanded list
        elif any(x in name_lower for x in [
            "water", "aqua", "glycerin", "glycerol", "aloe", "chamomile",
            "green tea", "vitamin e", "tocopherol", "vitamin c", "ascorbic",
            "hyaluronic", "niacinamide", "panthenol", "allantoin",
            "ceramide", "peptide", "squalane", "jojoba", "argan oil",
            "shea butter", "cocoa butter", "coconut oil", "olive oil",
            "sunflower", "safflower", "rosehip", "zinc oxide",
            "titanium dioxide", "kaolin", "bentonite", "xanthan gum",
            "guar gum", "cellulose", "starch", "beta-glucan",
            "citric acid", "lactic acid", "malic acid",
            "sodium chloride", "salt", "sucrose", "glucose",
            "caffeine", "retinol", "alpha hydroxy", "salicylic acid"
        ]):
            ewg_score = 1.0
            safety_label = "SAFE"
        
        # MODERATE (EWG 3-4) - common but with minor concerns
        elif any(x in name_lower for x in [
            "alcohol", "ethanol", "phenoxyethanol", "benzyl",
            "fragrance", "parfum", "dimethicone", "cyclopentasiloxane",
            "carbomer", "acrylate", "polymer", "copolymer",
            "sodium benzoate", "potassium sorbate", "citrus"
        ]):
            ewg_score = 3.0
            safety_label = "MODERATE"
        
        else:
            # Default based on family
            safety_label = "MODERATE" if ewg_score > 4 else "SAFE"

        # Determine comedogenic rating (0-5)
        comedogenic_rating = 2.0  # default
        if any(x in name_lower for x in ["coconut", "wheat germ", "flaxseed", "palm", "soybean"]):
            comedogenic_rating = 4.0
        elif any(x in name_lower for x in ["dimethicone", "silicone", "petrolatum", "mineral oil"]):
            comedogenic_rating = 3.0
        elif any(x in name_lower for x in ["jojoba", "argan", "squalane", "hemp seed", "rosehip"]):
            comedogenic_rating = 1.0
        elif any(x in name_lower for x in ["water", "glycerin", "hyaluronic", "niacinamide"]):
            comedogenic_rating = 0.0

        # Endocrine disruptor check
        is_endocrine_disruptor = any(x in name_lower for x in [
            "paraben", "phthalate", "oxybenzone", "triclosan",
            "bpa", "dioxin", "styrene", "pcb"
        ])

        # Pregnancy safety
        is_pregnancy_safe = not any(x in name_lower for x in [
            "retinol", "retinoic", "retinyl", "salicylic acid",
            "hydroquinone", "oxybenzone", "formaldehyde",
            "paraben", "phthalate", "triclosan"
        ])

        # Vegan check - expanded animal-derived ingredients
        is_vegan = not any(x in name_lower for x in [
            "lanolin", "beeswax", "collagen", "keratin", "elastin",
            "gelatin", "carmine", "cochineal", "guanine", "silk",
            "cashmere", "milk", "honey", "royal jelly", "propolis",
            "squalene", "tallow", "lard", "stearic acid", "cholesterol"
        ])

        return {
            "ingredient_name": name_lower,
            "ewg_score": ewg_score,
            "safety_label": safety_label,
            "chemical_family": chemical_family,
            "allergen": is_allergen,
            "comedogenic_rating": comedogenic_rating,
            "endocrine_disruptor": is_endocrine_disruptor,
            "pregnancy_safe": is_pregnancy_safe,
            "vegan": is_vegan,
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
            "safety_label": "UNKNOWN",
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
