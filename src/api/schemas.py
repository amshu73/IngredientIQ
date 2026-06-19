"""Pydantic v2 request/response schemas for the API."""

from typing import List, Optional

from pydantic import BaseModel, Field, validator


class BarcodeRequest(BaseModel):
    """Request body for barcode scanning endpoint."""

    barcode: str = Field(
        ...,
        min_length=8,
        max_length=14,
        description="Product barcode (EAN-13, EAN-8, UPC-A)",
        example="8901030859756",
    )
    user_profiles: List[str] = Field(
        default_factory=list,
        description="List of health profile tags",
        example=["SENSITIVE_SKIN", "PREGNANT"],
    )

    @validator("barcode")
    def validate_barcode(cls, v: str) -> str:
        """Validate barcode contains only digits."""
        if not v.isdigit():
            raise ValueError("Barcode must contain only digits")
        return v

    @validator("user_profiles")
    def validate_profiles(cls, v: List[str]) -> List[str]:
        """Validate profiles are uppercase."""
        valid_profiles = {
            "SENSITIVE_SKIN",
            "PREGNANT",
            "DIABETIC",
            "VEGAN",
            "NUT_ALLERGY",
            "FRAGRANCE_ALLERGY",
            "ACNE_PRONE",
        }
        for profile in v:
            if profile not in valid_profiles:
                raise ValueError(f"Unknown profile: {profile}")
        return v


class ImageRequest(BaseModel):
    """Request body for image-based ingredient extraction."""

    image_base64: str = Field(
        ...,
        min_length=100,
        description="Base64-encoded product label image",
    )
    user_profiles: List[str] = Field(
        default_factory=list,
        description="List of health profile tags",
    )

    @validator("user_profiles")
    def validate_profiles(cls, v: List[str]) -> List[str]:
        """Validate profiles are uppercase."""
        valid_profiles = {
            "SENSITIVE_SKIN",
            "PREGNANT",
            "DIABETIC",
            "VEGAN",
            "NUT_ALLERGY",
            "FRAGRANCE_ALLERGY",
            "ACNE_PRONE",
        }
        for profile in v:
            if profile not in valid_profiles:
                raise ValueError(f"Unknown profile: {profile}")
        return v


class ManualIngredientRequest(BaseModel):
    """Request body for manual ingredient list analysis."""

    product_name: Optional[str] = Field(
        default="Custom Product",
        description="Product name (optional)",
        example="My Moisturizer",
    )
    brand: Optional[str] = Field(
        default="Unknown Brand",
        description="Brand name (optional)",
        example="Brand X",
    )
    ingredients_text: str = Field(
        ...,
        min_length=3,
        description="Comma-separated list of ingredients",
        example="Water, Glycerin, Niacinamide, Phenoxyethanol, Fragrance",
    )
    user_profiles: List[str] = Field(
        default_factory=list,
        description="List of health profile tags",
        example=["SENSITIVE_SKIN"],
    )

    @validator("user_profiles")
    def validate_profiles(cls, v: List[str]) -> List[str]:
        """Validate profiles are uppercase."""
        valid_profiles = {
            "SENSITIVE_SKIN",
            "PREGNANT",
            "DIABETIC",
            "VEGAN",
            "NUT_ALLERGY",
            "FRAGRANCE_ALLERGY",
            "ACNE_PRONE",
        }
        for profile in v:
            if profile not in valid_profiles:
                raise ValueError(f"Unknown profile: {profile}")
        return v


class IngredientResult(BaseModel):
    """Safety assessment for a single ingredient."""

    name: str = Field(..., description="Ingredient name", example="Titanium Dioxide")
    safety_label: str = Field(
        ...,
        description="Safety classification",
        example="SAFE",
    )
    ewg_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="EWG hazard score (0=safe, 10=hazardous)",
        example=1.0,
    )
    chemical_family: str = Field(
        ...,
        description="Ingredient chemical family",
        example="colorant",
    )
    profile_warnings: List[str] = Field(
        default_factory=list,
        description="Health profiles this ingredient affects",
        example=["SENSITIVE_SKIN"],
    )
    explanation: str = Field(
        ...,
        description="Human-readable safety explanation",
        example="Essential inert mineral. No known hazards.",
    )


class ProfileWarning(BaseModel):
    """Warning about an ingredient for a specific user health profile."""

    ingredient: str = Field(
        ...,
        description="Ingredient name",
        example="Methylparaben",
    )
    profile: str = Field(
        ...,
        description="Health profile",
        example="PREGNANT",
    )
    severity: str = Field(
        ...,
        description="Warning severity level",
        example="CAUTION",
    )
    message: str = Field(
        ...,
        description="Detailed warning message",
        example="Parabens may have weak endocrine effects. Limited pregnancy data.",
    )


class ProductSafetyResponse(BaseModel):
    """Complete product safety assessment response."""

    product_name: str = Field(
        ...,
        description="Product name",
        example="Himalaya Moisturizing Aloe Vera Face Wash",
    )
    brand: str = Field(
        ..., description="Brand name", example="Himalaya"
    )
    grade: str = Field(
        ...,
        description="Overall safety grade (A-F)",
        example="B",
    )
    overall_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Numeric safety score (0=hazardous, 10=safe)",
        example=7.4,
    )
    ingredient_count: int = Field(
        ...,
        ge=0,
        description="Total number of ingredients",
        example=18,
    )
    ingredients: List[IngredientResult] = Field(
        ...,
        description="Detailed results for each ingredient",
    )
    worst_ingredients: List[str] = Field(
        ...,
        description="Top concerning ingredients",
        example=["Methylparaben", "Fragrance"],
    )
    profile_warnings: List[ProfileWarning] = Field(
        default_factory=list,
        description="Warnings matching user health profiles",
    )
    recommendation: str = Field(
        ...,
        description="Overall product recommendation",
        example="Generally safe product. 2 ingredients flagged for your profiles.",
    )
    scan_method: str = Field(
        ...,
        description="How product was scanned (barcode or ocr)",
        example="barcode",
    )


class HealthProfile(BaseModel):
    """Description of available health profile."""

    profile: str = Field(
        ..., description="Profile identifier", example="SENSITIVE_SKIN"
    )
    description: str = Field(
        ...,
        description="Profile description",
        example="Easily irritated skin prone to reactions",
    )


class GradeExplanation(BaseModel):
    """Explanation of safety grades."""

    grade: str = Field(..., description="Grade letter", example="A")
    numeric_score_range: str = Field(
        ..., description="Numeric score range", example="9.0-10.0"
    )
    meaning: str = Field(
        ...,
        description="What this grade means",
        example="All ingredients SAFE, no profile warnings",
    )
    recommendation_level: str = Field(
        ..., description="Recommendation level", example="✅ Excellent to use"
    )


class HealthStatus(BaseModel):
    """API health status response."""

    status: str = Field(..., example="healthy")
    models_loaded: bool = Field(..., example=True)
    version: str = Field(..., example="1.0.0")
    message: str = Field(..., example="API is ready to process requests")
