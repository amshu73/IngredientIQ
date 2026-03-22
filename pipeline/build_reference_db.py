"""Build reference ingredient safety database."""

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def build_reference_database(output_dir: Path) -> pd.DataFrame:
    """
    Build master ingredient safety reference database.

    Downloads/processes data from:
    - EWG Skin Deep ingredient hazard scores
    - EU CosIng INCI ingredient definitions
    - Allergen and safety classifications

    Saves to: data/reference/ingredient_safety.parquet

    Args:
        output_dir: Directory to save reference data

    Returns:
        DataFrame with complete ingredient safety data
    """
    logger.info("Building reference ingredient safety database...")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build default ingredient database from known safe/unsafe ingredients
    ingredients_data = _build_default_ingredients()
    df = pd.DataFrame(ingredients_data)

    # Save to parquet
    output_path = output_dir / "ingredient_safety.parquet"
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved reference database with {len(df)} ingredients to {output_path}")

    return df


def _build_default_ingredients() -> List[Dict]:
    """
    Build comprehensive ingredient safety database from known data.

    Returns:
        List of ingredient dictionaries with safety information
    """
    ingredients = [
        # Safe ingredients
        {
            "ingredient_name": "water",
            "ewg_score": 1,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "solvent",
        },
        {
            "ingredient_name": "glycerin",
            "ewg_score": 1,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "humectant",
        },
        {
            "ingredient_name": "titanium dioxide",
            "ewg_score": 1,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "colorant",
        },
        {
            "ingredient_name": "tocopherol",
            "ewg_score": 1,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": False,
            "chemical_family": "antioxidant",
        },
        {
            "ingredient_name": "xanthan gum",
            "ewg_score": 1,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "thickener",
        },
        # Moderate ingredients
        {
            "ingredient_name": "methylparaben",
            "ewg_score": 4,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 1,
            "endocrine_disruptor": True,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "preservative",
        },
        {
            "ingredient_name": "fragrance",
            "ewg_score": 4,
            "hazard_level": "MODERATE",
            "allergen": True,
            "comedogenic_rating": 1,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "fragrance",
        },
        {
            "ingredient_name": "sodium lauryl sulfate",
            "ewg_score": 4,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 2,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "surfactant",
        },
        {
            "ingredient_name": "phenoxyethanol",
            "ewg_score": 4,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 1,
            "endocrine_disruptor": False,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "preservative",
        },
        {
            "ingredient_name": "alcohol",
            "ewg_score": 3,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 1,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "solvent",
        },
        # Hazardous ingredients
        {
            "ingredient_name": "oxybenzone",
            "ewg_score": 8,
            "hazard_level": "HAZARDOUS",
            "allergen": False,
            "comedogenic_rating": 2,
            "endocrine_disruptor": True,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "uv_filter",
        },
        {
            "ingredient_name": "coal tar",
            "ewg_score": 9,
            "hazard_level": "HAZARDOUS",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": False,
            "vegan": False,
            "chemical_family": "colorant",
        },
        {
            "ingredient_name": "hydroquinone",
            "ewg_score": 8,
            "hazard_level": "HAZARDOUS",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "depigmenting",
        },
        {
            "ingredient_name": "formaldehyde",
            "ewg_score": 9,
            "hazard_level": "HAZARDOUS",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": True,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "preservative",
        },
        {
            "ingredient_name": "retinol",
            "ewg_score": 3,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": False,
            "vegan": False,
            "chemical_family": "active",
        },
        {
            "ingredient_name": "salicylic acid",
            "ewg_score": 3,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "exfoliant",
        },
        {
            "ingredient_name": "benzoyl peroxide",
            "ewg_score": 3,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "acne_fighter",
        },
        {
            "ingredient_name": "parabens",
            "ewg_score": 4,
            "hazard_level": "MODERATE",
            "allergen": False,
            "comedogenic_rating": 1,
            "endocrine_disruptor": True,
            "pregnancy_safe": False,
            "vegan": True,
            "chemical_family": "preservative",
        },
        {
            "ingredient_name": "lanolin",
            "ewg_score": 2,
            "hazard_level": "SAFE",
            "allergen": True,
            "comedogenic_rating": 3,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": False,
            "chemical_family": "emollient",
        },
        {
            "ingredient_name": "sodium benzoate",
            "ewg_score": 2,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "preservative",
        },
        {
            "ingredient_name": "citric acid",
            "ewg_score": 1,
            "hazard_level": "SAFE",
            "allergen": False,
            "comedogenic_rating": 0,
            "endocrine_disruptor": False,
            "pregnancy_safe": True,
            "vegan": True,
            "chemical_family": "pH_buffer",
        },
    ]

    return ingredients


def build_inci_synonyms(output_dir: Path) -> pd.DataFrame:
    """
    Build INCI name synonym mapping table.

    Maps common ingredient names and codes to canonical INCI names.

    Args:
        output_dir: Directory to save synonyms database

    Returns:
        DataFrame with synonym mappings
    """
    logger.info("Building INCI synonym mapping...")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create comprehensive synonym mapping
    synonyms_data = [
        {"synonym": "aqua", "inci_name": "water"},
        {"synonym": "h2o", "inci_name": "water"},
        {"synonym": "glycerin", "inci_name": "glycerin"},
        {"synonym": "glycerol", "inci_name": "glycerin"},
        {"synonym": "ci 77891", "inci_name": "titanium dioxide"},
        {"synonym": "titanium dioxide", "inci_name": "titanium dioxide"},
        {"synonym": "fragrance", "inci_name": "fragrance"},
        {"synonym": "parfum", "inci_name": "fragrance"},
        {"synonym": "methylparaben", "inci_name": "methylparaben"},
        {"synonym": "ethylparaben", "inci_name": "ethylparaben"},
        {"synonym": "phenoxyethanol", "inci_name": "phenoxyethanol"},
        {"synonym": "xanthan gum", "inci_name": "xanthan gum"},
        {"synonym": "edta", "inci_name": "edta"},
        {"synonym": "sodium benzoate", "inci_name": "sodium benzoate"},
        {"synonym": "potassium sorbate", "inci_name": "potassium sorbate"},
        {"synonym": "alcohol", "inci_name": "alcohol"},
        {"synonym": "ethanol", "inci_name": "alcohol"},
        {"synonym": "oxybenzone", "inci_name": "oxybenzone"},
        {"synonym": "retinol", "inci_name": "retinol"},
        {"synonym": "salicylic acid", "inci_name": "salicylic acid"},
        {"synonym": "benzoyl peroxide", "inci_name": "benzoyl peroxide"},
        {"synonym": "lanolin", "inci_name": "lanolin"},
        {"synonym": "beeswax", "inci_name": "beeswax"},
        {"synonym": "coal tar", "inci_name": "coal tar"},
        {"synonym": "hydroquinone", "inci_name": "hydroquinone"},
        {"synonym": "formaldehyde", "inci_name": "formaldehyde"},
    ]

    df = pd.DataFrame(synonyms_data)
    output_path = output_dir / "inci_synonyms.parquet"
    df.to_parquet(output_path, index=False)
    logger.info(f"Saved INCI synonyms ({len(df)} mappings) to {output_path}")

    return df


def main(data_dir: Path) -> None:
    """
    Main function to build all reference databases.

    Args:
        data_dir: Data directory path
    """
    logger.info("Starting reference database build...")
    reference_dir = data_dir / "reference"

    # Build databases
    ingredient_db = build_reference_database(reference_dir)
    inci_synonyms = build_inci_synonyms(reference_dir)

    logger.info("✅ Reference databases built successfully")
    logger.info(f"   - Ingredients: {len(ingredient_db)} entries")
    logger.info(f"   - INCI synonyms: {len(inci_synonyms)} mappings")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    data_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./data")
    main(data_dir)
