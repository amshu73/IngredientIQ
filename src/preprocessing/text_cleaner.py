"""Text cleaning and preprocessing for raw ingredient labels."""

import logging
import re
import unicodedata
from typing import List

logger = logging.getLogger(__name__)


def clean_ingredient_string(text: str) -> str:
    """
    Clean raw ingredient string by removing artifacts and normalizing.

    Operations:
    - Remove percentages (e.g., "water 80%")
    - Remove trademark/copyright symbols (®, ©, ™)
    - Remove "may contain" statements
    - Remove claims in brackets
    - Remove asterisks and special markers
    - Normalize unicode (e.g., Hindi characters)
    - Convert to lowercase
    - Remove extra whitespace

    Args:
        text: Raw ingredient text string

    Returns:
        Cleaned ingredient string

    Example:
        "WATER* (80%), Glycerin® - may contain nuts [non-GMO]"
        -> "water, glycerin"
    """
    if not isinstance(text, str):
        return ""

    # Remove unicode formatting marks but keep base characters
    text = unicodedata.normalize("NFKD", text)

    # Remove trademark/copyright symbols
    text = re.sub(r"[®©™Ⓡ]", "", text)

    # Remove "may contain" statements
    text = re.sub(r"may\s+contain.*?(?=,|$|\.)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(.*?may\s+contain.*?\)", "", text, flags=re.IGNORECASE)

    # Remove bracketed claims
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?(?:non-gmo|organic|natural|vegan|gluten|soy|nut).*?\)", "", text, flags=re.IGNORECASE)

    # Remove percentages and numeric values (but keep in ingredient names like "5-htp")
    text = re.sub(r"\b\d+\s*%\b", "", text)  # "80%" -> ""
    text = re.sub(r"(?<![a-zA-Z])\d+(?![a-zA-Z])\s*(?:[a-z]{1,3}\b)?", "", text)  # "80 mg" -> ""

    # Remove asterisks, daggers, and other markers
    text = re.sub(r"[*†‡§¶]", "", text)

    # Remove extra symbols but keep hyphens in compound names
    text = re.sub(r"[^\w\s,\-]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Convert to lowercase
    text = text.lower()

    # Remove common English stop words in ingredient labels
    stop_words = {
        "and", "or", "the", "a", "an", "with", "from", "to",
        "derived", "from", "extract", "oil", "juice", "powder"
    }

    # Only remove if they appear to be standalone words - not part of ingredient names
    words = text.split()
    filtered_words = [
        w for w in words 
        if w not in stop_words or len(w) > 3
    ]
    text = " ".join(filtered_words)

    # Final cleanup of extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    logger.debug(f"Cleaned ingredient string: {len(text)} chars, {len(text.split(','))} potential ingredients")
    return text


def clean_ingredient_name(name: str) -> str:
    """
    Clean single ingredient name string.

    Removes:
    - Leading/trailing whitespace
    - Parenthetical information
    - Percentage values
    - Trademark symbols
    - Special characters

    Args:
        name: Single ingredient name

    Returns:
        Cleaned ingredient name

    Example:
        "Titanium Dioxide (CI 77891) - 5%" -> "titanium dioxide ci 77891"
    """
    if not isinstance(name, str):
        return ""

    # Remove parenthetical content but try to preserve useful info like "CI 77891"
    # Special handling: keep "CI XXXXX" format
    ci_match = re.search(r"CI\s+\d+", name, flags=re.IGNORECASE)
    ci_code = ci_match.group() if ci_match else None

    # Remove all parentheses content
    name = re.sub(r"\([^)]*\)", "", name)

    # Add back CI code if present
    if ci_code:
        name = f"{name.strip()} {ci_code}"

    # Remove percentages
    name = re.sub(r"\d+\s*%", "", name)

    # Remove trademark symbols
    name = re.sub(r"[®©™]", "", name)

    # Remove asterisks and markers
    name = re.sub(r"[*†‡§]", "", name)

    # Remove special characters
    name = re.sub(r"[^\w\s\-]", "", name)

    # Normalize whitespace and lowercase
    name = re.sub(r"\s+", " ", name).strip().lower()

    return name


def normalize_multilingual_text(text: str) -> str:
    """
    Normalize multilingual text (e.g., Hindi/English mixture).

    Preserves Latin characters and whitespace, removes diacritics.

    Args:
        text: Potentially multilingual text

    Returns:
        Normalized text with non-Latin scripts removed/transliterated

    Example:
        "पानी (Aqua) - जल" -> "aqua"
    """
    if not isinstance(text, str):
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)

    # Remove non-ASCII characters except common symbols
    text = text.encode("ascii", "ignore").decode("ascii")

    # Clean up the result
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_potential_ingredients(text: str) -> List[str]:
    """
    Extract potential ingredient names from raw text.

    Splits on commas and common separators, cleans each potential ingredient.

    Args:
        text: Raw ingredient text

    Returns:
        List of cleaned potential ingredient names

    Example:
        "Water, Glycerin (80%), Fragrance* - may contain nuts"
        -> ["water", "glycerin", "fragrance"]
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Clean the entire string first
    text = clean_ingredient_string(text)

    # Split on various separators
    ingredients = re.split(r"[,;/]", text)

    # Clean each ingredient
    cleaned = []
    for ingredient in ingredients:
        cleaned_name = clean_ingredient_name(ingredient.strip())
        if cleaned_name and len(cleaned_name) > 2:  # Skip very short strings
            cleaned.append(cleaned_name)

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for ing in cleaned:
        if ing not in seen:
            unique.append(ing)
            seen.add(ing)

    logger.debug(f"Extracted {len(unique)} potential ingredients")
    return unique
