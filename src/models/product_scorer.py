"""Product-level safety grading algorithm."""

import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

from src.models.profile_matcher import ProfileMatcher, WarningMessage

logger = logging.getLogger(__name__)


@dataclass
class IngredientResult:
    """Safety assessment result for a single ingredient."""

    name: str
    safety_label: str
    ewg_score: float
    chemical_family: str
    profile_warnings: List[str]
    explanation: str


@dataclass
class ProductGrade:
    """Overall product safety assessment result."""

    product_name: str
    brand: str
    grade: str  # A-F
    overall_score: float  # 0-10
    ingredient_count: int
    ingredients: List[Dict]
    worst_ingredients: List[str]
    profile_warnings: List[Dict]
    recommendation: str
    scan_method: str


class ProductScorer:
    """Computes overall product safety grade (A-F) from ingredient assessments."""

    def __init__(self) -> None:
        """Initialize product scorer."""
        self.profile_matcher = ProfileMatcher()
        logger.info("Initialized ProductScorer")

        # Ingredient safety levels that warrant avoidance
        self.banned_ingredients = {
            "lead",
            "mercury",
            "asbestos",
            "hydroquinone",
            "mercury compounds",
            "formaldehyde",
            "chlorofluorocarbon",
        }

    def score_product(
        self,
        product_name: str,
        brand: str,
        ingredients: List[str],
        ingredient_features: Dict[str, dict],
        profiles: List[str],
        scan_method: str = "unknown",
    ) -> ProductGrade:
        """
        Score product overall safety and assign A-F grade.

        Algorithm:
        - A: All ingredients SAFE, no profile warnings
        - B: Mostly safe, 1-2 moderate ingredients, no hazardous
        - C: Several moderate ingredients OR 1 hazardous
        - D: Multiple hazardous ingredients
        - F: Contains banned/toxic ingredients

        Args:
            product_name: Product name
            brand: Brand name
            ingredients: List of normalized ingredient names
            ingredient_features: Dict of ingredient -> feature dict
                                (must include 'safety_label', 'ewg_score')
            profiles: List of user health profile strings
            scan_method: "barcode" or "ocr"

        Returns:
            ProductGrade dataclass with all scoring details
        """
        logger.info(f"Scoring product: {product_name} with {len(ingredients)} ingredients")

        # Check for banned ingredients
        banned_found = self._check_banned(ingredients)
        if banned_found:
            logger.warning(f"Product contains banned ingredients: {banned_found}")
            return self._create_result_grade(
                product_name=product_name,
                brand=brand,
                grade="F",
                overall_score=0.0,
                ingredient_count=len(ingredients),
                ingredients=ingredients,
                ingredient_features=ingredient_features,
                profiles=profiles,
                worst_ingredients=banned_found,
                profile_warnings=[],
                recommendation="⛔ Contains banned or highly toxic ingredients. DO NOT USE.",
                scan_method=scan_method,
            )

        # Classify ingredients
        safe_count, moderate_count, hazardous_count, unknown_count = (
            self._classify_ingredients(ingredients, ingredient_features)
        )

        # Get worst ingredients
        worst_ingredients = self._get_worst_ingredients(
            ingredients, ingredient_features, top_n=3
        )

        # Get profile-based warnings
        profile_warnings = self._get_profile_warnings(
            ingredients, profiles
        )

        # Determine grade
        grade, numeric_score = self._determine_grade(
            safe_count=safe_count,
            moderate_count=moderate_count,
            hazardous_count=hazardous_count,
            profile_warning_count=len(
                set((w.ingredient, w.profile) for w in profile_warnings)
            ),
            total_ingredients=len(ingredients),
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            grade=grade,
            worst_ingredients=worst_ingredients,
            profile_warnings=profile_warnings,
            hazardous_count=hazardous_count,
        )

        logger.info(f"Product scored: Grade {grade} (score: {numeric_score:.1f}/10)")

        return self._create_result_grade(
            product_name=product_name,
            brand=brand,
            grade=grade,
            overall_score=numeric_score,
            ingredient_count=len(ingredients),
            ingredients=ingredients,
            ingredient_features=ingredient_features,
            profiles=profiles,
            worst_ingredients=worst_ingredients,
            profile_warnings=profile_warnings,
            recommendation=recommendation,
            scan_method=scan_method,
        )

    def _check_banned(self, ingredients: List[str]) -> List[str]:
        """Check for banned or highly toxic ingredients."""
        found = []
        for ingredient in ingredients:
            if any(ban in ingredient.lower() for ban in self.banned_ingredients):
                found.append(ingredient)
        return found

    @staticmethod
    def _classify_ingredients(
        ingredients: List[str],
        features: Dict[str, dict],
    ) -> Tuple[int, int, int, int]:
        """Count ingredients by safety category."""
        safe = moderate = hazardous = unknown = 0

        for ingredient in ingredients:
            feature_dict = features.get(ingredient, {})
            label = feature_dict.get("safety_label", "UNKNOWN")

            if label == "SAFE":
                safe += 1
            elif label == "MODERATE":
                moderate += 1
            elif label == "HAZARDOUS":
                hazardous += 1
            else:
                unknown += 1

        return safe, moderate, hazardous, unknown

    @staticmethod
    def _get_worst_ingredients(
        ingredients: List[str],
        features: Dict[str, dict],
        top_n: int = 3,
    ) -> List[str]:
        """Get top N ingredients by hazard level and EWG score."""
        # Map ingredients to (hazard_priority, ewg_score)
        scored = []
        for ingredient in ingredients:
            feature_dict = features.get(ingredient, {})
            label = feature_dict.get("safety_label", "UNKNOWN")
            ewg_score = feature_dict.get("ewg_score", 5.0)

            # Hazard priority: HAZARDOUS > MODERATE > UNKNOWN > SAFE
            priority = {"HAZARDOUS": 3, "MODERATE": 2, "UNKNOWN": 1, "SAFE": 0}
            hazard_priority = priority.get(label, 0)

            scored.append((ingredient, hazard_priority, ewg_score))

        # Sort by hazard_priority DESC, then ewg_score DESC
        scored.sort(key=lambda x: (-x[1], -x[2]))

        return [ing[0] for ing in scored[:top_n]]

    def _get_profile_warnings(
        self,
        ingredients: List[str],
        profiles: List[str],
    ) -> List[WarningMessage]:
        """Get warnings for user health profiles."""
        warnings = self.profile_matcher.match_product(ingredients, profiles)
        # Sort by severity (AVOID > WARNING > CAUTION)
        severity_order = {"AVOID": 3, "WARNING": 2, "CAUTION": 1}
        warnings.sort(
            key=lambda w: -severity_order.get(w.severity, 0)
        )
        return warnings

    @staticmethod
    def _determine_grade(
        safe_count: int,
        moderate_count: int,
        hazardous_count: int,
        profile_warning_count: int,
        total_ingredients: int,
    ) -> Tuple[str, float]:
        """
        Determine product safety grade (A-F) based on ingredient counts.

        Returns:
            Tuple of (grade_letter, numeric_score_0_to_10)
        """
        # Grade F: Any hazardous ingredients
        if hazardous_count >= 2:
            return "F", 2.0

        # Grade D: 1 hazardous OR many moderate
        if hazardous_count == 1 or moderate_count >= 5:
            return "D", 3.5

        # Grade C: 3-4 moderate ingredients or significant profile issues
        if moderate_count >= 3 or (moderate_count >= 2 and profile_warning_count >= 2):
            return "C", 5.5

        # Grade B: 1-2 moderate, some profile concerns
        if moderate_count >= 1:
            return "B", 7.5

        # Grade A: All safe, no profile warnings
        if profile_warning_count == 0 and hazardous_count == 0:
            return "A", 9.0

        # Default to B
        return "B", 7.5

    @staticmethod
    def _generate_recommendation(
        grade: str,
        worst_ingredients: List[str],
        profile_warnings: List[WarningMessage],
        hazardous_count: int,
    ) -> str:
        """Generate human-readable safety recommendation."""
        if grade == "F":
            return "⛔ AVOID. Contains toxic or banned ingredients. Do not use."

        if grade == "D":
            worst_str = ", ".join(worst_ingredients[:2])
            return f"⚠️ CAUTION. Found {hazardous_count} concerning ingredient(s): {worst_str}. Patch test before use."

        if grade == "C":
            worst_str = ", ".join(worst_ingredients[:2])
            msg = f"Several potentially irritating ingredients found: {worst_str}."
            if profile_warnings:
                msg += f" {len(profile_warnings)} warnings for your health profile(s)."
            return msg

        if grade == "B":
            msg = "Generally safe product."
            if len(worst_ingredients) > 0:
                msg += f" {len(worst_ingredients)} ingredient(s) to watch: {worst_ingredients[0]}."
            if profile_warnings:
                msg += f" {len(profile_warnings)} matching your health profile(s)."
            msg += " Patch test if sensitive."
            return msg

        # Grade A
        return "✅ Excellent ingredient profile. Low-risk product."

    @staticmethod
    def _create_result_grade(
        product_name: str,
        brand: str,
        grade: str,
        overall_score: float,
        ingredient_count: int,
        ingredients: List[str],
        ingredient_features: Dict[str, dict],
        profiles: List[str],
        worst_ingredients: List[str],
        profile_warnings: List[WarningMessage],
        recommendation: str,
        scan_method: str,
    ) -> ProductGrade:
        """Create ProductGrade result object."""
        # Build ingredient result list
        ingredient_results = []
        for ingredient in ingredients:
            feature_dict = ingredient_features.get(ingredient, {})
            warnings = [w.severity for w in profile_warnings if w.ingredient == ingredient]

            ingredient_results.append({
                "name": ingredient,
                "safety_label": feature_dict.get("safety_label", "UNKNOWN"),
                "ewg_score": float(feature_dict.get("ewg_score", 5.0)),
                "chemical_family": feature_dict.get("chemical_family", "unknown"),
                "profile_warnings": list(dict.fromkeys(warnings)),  # unique warnings
                "explanation": f"{ingredient} (EWG: {feature_dict.get('ewg_score', 5.0):.0f})",
            })

        # Build profile warnings list for response
        profile_warning_results = []
        for warning in profile_warnings:
            profile_warning_results.append({
                "ingredient": warning.ingredient,
                "profile": warning.profile.value,
                "severity": warning.severity,
                "message": warning.message,
            })

        return ProductGrade(
            product_name=product_name,
            brand=brand,
            grade=grade,
            overall_score=overall_score,
            ingredient_count=ingredient_count,
            ingredients=ingredient_results,
            worst_ingredients=worst_ingredients,
            profile_warnings=profile_warning_results,
            recommendation=recommendation,
            scan_method=scan_method,
        )
