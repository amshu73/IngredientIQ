"""Profile-based ingredient warning matcher for health conditions."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthProfile(str, Enum):
    """Supported health profiles for personalized warnings."""

    SENSITIVE_SKIN = "SENSITIVE_SKIN"
    PREGNANT = "PREGNANT"
    DIABETIC = "DIABETIC"
    VEGAN = "VEGAN"
    NUT_ALLERGY = "NUT_ALLERGY"
    FRAGRANCE_ALLERGY = "FRAGRANCE_ALLERGY"
    ACNE_PRONE = "ACNE_PRONE"


@dataclass
class WarningMessage:
    """A warning about an ingredient for a specific profile."""

    ingredient: str
    profile: HealthProfile
    severity: str  # "CAUTION", "WARNING", "AVOID"
    message: str


class ProfileMatcher:
    """Matches ingredient risks to user health profiles."""

    def __init__(self) -> None:
        """Initialize profile matcher with rule definitions."""
        self.rules = self._build_rules()
        logger.info(f"Initialized ProfileMatcher with {len(self.rules)} rules")

    def _build_rules(self) -> Dict[HealthProfile, Dict[str, dict]]:
        """
        Build mapping of profile -> ingredient -> warning info.

        Returns:
            Nested dictionary structure for efficient lookup
        """
        return {
            HealthProfile.SENSITIVE_SKIN: {
                "fragrance": {
                    "severity": "WARNING",
                    "message": "Fragrance is a common irritant for sensitive skin. May cause redness, itching, or burning.",
                },
                "alcohol": {
                    "severity": "WARNING",
                    "message": "Alcohol can dry out and irritate sensitive skin.",
                },
                "oxybenzone": {
                    "severity": "WARNING",
                    "message": "Strong UV filter that may trigger sensitive skin reactions.",
                },
                "phenoxyethanol": {
                    "severity": "CAUTION",
                    "message": "Preservative that may cause irritation in sensitive individuals.",
                },
                "essential oil": {
                    "severity": "CAUTION",
                    "message": "Essential oils can irritate sensitive skin despite natural origin.",
                },
                "sodium lauryl sulfate": {
                    "severity": "WARNING",
                    "message": "Strong surfactant known to strip skin and cause irritation.",
                },
                "benzoyl peroxide": {
                    "severity": "CAUTION",
                    "message": "Can cause dryness and irritation, start with low concentration.",
                },
                "retinol": {
                    "severity": "CAUTION",
                    "message": "Retinol can cause redness and sensitivity; use low doses initially.",
                },
            },
            HealthProfile.PREGNANT: {
                "retinol": {
                    "severity": "AVOID",
                    "message": "Retinoids may increase birth defect risk. Avoid in first trimester and limit throughout pregnancy.",
                },
                "retinaldehyde": {
                    "severity": "AVOID",
                    "message": "Retinol derivative - same risk as retinol during pregnancy.",
                },
                "salicylic acid": {
                    "severity": "CAUTION",
                    "message": "High doses of salicylic acid may pose risks. Limit topical use.",
                },
                "benzoyl peroxide": {
                    "severity": "CAUTION",
                    "message": "Generally safe but some caution recommended during pregnancy.",
                },
                "parabens": {
                    "severity": "CAUTION",
                    "message": "Parabens may have weak endocrine effects. Limited pregnancy data - consider alternatives.",
                },
                "methylparaben": {
                    "severity": "CAUTION",
                    "message": "Weak endocrine disruptor activity. Limited studies in pregnancy - consider alternatives.",
                },
                "phthalates": {
                    "severity": "WARNING",
                    "message": "Phthalates may affect fetal development. Avoid products with these plasticizers.",
                },
                "hydroquinone": {
                    "severity": "WARNING",
                    "message": "Skin lightening agent with limited pregnancy safety data. Best avoided.",
                },
            },
            HealthProfile.DIABETIC: {
                "glycerin": {
                    "severity": "CAUTION",
                    "message": "Diabetics with tight glucose control should monitor glycerin in topicals.",
                },
                "sugar-based": {
                    "severity": "CAUTION",
                    "message": "Sugar alcohols and sweeteners in topicals may interfere with glucose management.",
                },
            },
            HealthProfile.VEGAN: {
                "lanolin": {
                    "severity": "WARNING",
                    "message": "Lanolin is derived from sheep wool. Not vegan.",
                },
                "beeswax": {
                    "severity": "WARNING",
                    "message": "Beeswax is a bee product. Not suitable for vegan lifestyles.",
                },
                "carmine": {
                    "severity": "WARNING",
                    "message": "Carmine is derived from insects (cochineal). Not vegan.",
                },
                "collagen": {
                    "severity": "WARNING",
                    "message": "Collagen is typically derived from animals. Choose plant-based alternatives.",
                },
                "keratin": {
                    "severity": "WARNING",
                    "message": "Keratin is usually animal-derived (from feathers/horns). Check source.",
                },
                "squalane": {
                    "severity": "CAUTION",
                    "message": "Squalane may be shark-derived (though plant sources exist). Verify sourcing.",
                },
                "shellac": {
                    "severity": "WARNING",
                    "message": "Shellac is derived from lac beetles. Not vegan.",
                },
            },
            HealthProfile.NUT_ALLERGY: {
                "almond oil": {
                    "severity": "AVOID",
                    "message": "Almond oil can trigger nut allergies even through topical application.",
                },
                "jojoba oil": {
                    "severity": "CAUTION",
                    "message": "Jojoba is not a nut but may cross-contaminate. Check labels.",
                },
                "shea butter": {
                    "severity": "CAUTION",
                    "message": "Shea is not a true nut but may be contaminated. Verify processing.",
                },
            },
            HealthProfile.FRAGRANCE_ALLERGY: {
                "fragrance": {
                    "severity": "AVOID",
                    "message": "Choose fragrance-free products to avoid allergic reactions.",
                },
                "parfum": {
                    "severity": "AVOID",
                    "message": "Parfum/Fragrance is the primary allergen. Avoid entirely.",
                },
                "essential oil": {
                    "severity": "WARNING",
                    "message": "Essential oils are natural fragrances that can trigger allergic reactions.",
                },
                "linalool": {
                    "severity": "CAUTION",
                    "message": "Linalool is an EU-listed allergen found in fragrances.",
                },
                "limonene": {
                    "severity": "CAUTION",
                    "message": "Limonene is an EU-listed allergen, oxidizes on exposure to air.",
                },
            },
            HealthProfile.ACNE_PRONE: {
                "comedogenic": {
                    "severity": "WARNING",
                    "message": "Highly comedogenic ingredients can clog pores and worsen acne.",
                },
                "coconut oil": {
                    "severity": "WARNING",
                    "message": "Coconut oil is highly comedogenic (ratings 4-5). Avoid on face.",
                },
                "lanolin": {
                    "severity": "CAUTION",
                    "message": "Lanolin is moderately comedogenic (rating 3). May worsen acne.",
                },
                "fragrance": {
                    "severity": "CAUTION",
                    "message": "Fragrance can irritate acne-prone skin and trigger breakouts.",
                },
                "silicones": {
                    "severity": "CAUTION",
                    "message": "Silicones can trap bacteria and potentially worsen acne.",
                },
                "benzoyl peroxide": {
                    "severity": "CAUTION",
                    "message": "Effective for acne but can cause irritation. Use with caution and moisturizer.",
                },
            },
        }

    def match_profile(
        self,
        ingredient: str,
        profiles: List[str],
    ) -> List[WarningMessage]:
        """
        Match ingredient against user health profiles.

        Checks if ingredient triggers any warnings for the specified profiles.

        Args:
            ingredient: Normalized ingredient name
            profiles: List of health profile strings (e.g., ["SENSITIVE_SKIN", "PREGNANT"])

        Returns:
            List of WarningMessage objects for triggered warnings
        """
        warnings = []
        ingredient_lower = ingredient.lower()

        for profile_str in profiles:
            try:
                profile = HealthProfile[profile_str]
            except KeyError:
                logger.warning(f"Unknown profile: {profile_str}")
                continue

            # Get rules for this profile
            profile_rules = self.rules.get(profile, {})

            # Check if ingredient matches any rule trigger
            for trigger, rule_info in profile_rules.items():
                if trigger in ingredient_lower or ingredient_lower in trigger:
                    warnings.append(
                        WarningMessage(
                            ingredient=ingredient,
                            profile=profile,
                            severity=rule_info["severity"],
                            message=rule_info["message"],
                        )
                    )

        return warnings

    def match_product(
        self,
        ingredients: List[str],
        profiles: List[str],
    ) -> List[WarningMessage]:
        """
        Match all ingredients in a product against health profiles.

        Args:
            ingredients: List of product ingredient names
            profiles: List of user health profile strings

        Returns:
            List of all WarningMessage objects
        """
        all_warnings = []

        for ingredient in ingredients:
            warnings = self.match_profile(ingredient, profiles)
            all_warnings.extend(warnings)

        # Remove duplicates
        unique_warnings = {}
        for warning in all_warnings:
            key = (warning.ingredient, warning.profile.value)
            # Keep the most severe warning
            if key not in unique_warnings or self._severity_rank(
                warning.severity
            ) > self._severity_rank(unique_warnings[key].severity):
                unique_warnings[key] = warning

        return list(unique_warnings.values())

    @staticmethod
    def _severity_rank(severity: str) -> int:
        """Get numeric rank for severity level (higher = more severe)."""
        ranks = {"CAUTION": 1, "WARNING": 2, "AVOID": 3}
        return ranks.get(severity, 0)

    def get_profile_description(self, profile: str) -> str:
        """Get human-readable description of a health profile."""
        descriptions = {
            HealthProfile.SENSITIVE_SKIN: "Easily irritated skin prone to reactions",
            HealthProfile.PREGNANT: "Pregnant or planning pregnancy",
            HealthProfile.DIABETIC: "Diabetes diagnosis or glucose monitoring",
            HealthProfile.VEGAN: "Plant-based / no animal-derived ingredients",
            HealthProfile.NUT_ALLERGY: "Nut allergy (including tree nuts)",
            HealthProfile.FRAGRANCE_ALLERGY: "Fragrance sensitivity or allergic reactions",
            HealthProfile.ACNE_PRONE: "Acne-prone or congestion-prone skin",
        }
        try:
            prof = HealthProfile[profile]
            return descriptions.get(prof, "Unknown profile")
        except KeyError:
            return "Unknown profile"

    @staticmethod
    def get_all_profiles() -> List[str]:
        """Return list of all available health profiles."""
        return [p.value for p in HealthProfile]
