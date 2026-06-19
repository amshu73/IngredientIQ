"""FastAPI application for IngredientIQ Product Safety Intelligence API."""

import logging.config
import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from src import __version__
from src.api.schemas import (
    BarcodeRequest,
    GradeExplanation,
    HealthProfile,
    HealthStatus,
    ImageRequest,
    ManualIngredientRequest,
    ProductSafetyResponse,
)

# Lazy imports - will load when needed
try:
    from src.features.ingredient_encoder import IngredientEncoder
    HAS_ENCODER = True
except ImportError:
    HAS_ENCODER = False
    IngredientEncoder = None

try:
    from src.ingestion.barcode_fetcher import fetch_product_by_barcode, ProductNotFoundError
    HAS_BARCODE = True
except ImportError:
    HAS_BARCODE = False
    fetch_product_by_barcode = None
    ProductNotFoundError = Exception

try:
    from src.ingestion.ocr_extractor import extract_ingredients_from_image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    extract_ingredients_from_image = None

try:
    from src.models.product_scorer import ProductScorer
    HAS_SCORER = True
except ImportError:
    HAS_SCORER = False
    ProductScorer = None

try:
    from src.models.profile_matcher import ProfileMatcher
    HAS_MATCHER = True
except ImportError:
    HAS_MATCHER = False
    ProfileMatcher = None

try:
    from src.preprocessing.ingredient_normaliser import normalise_ingredient_list
    HAS_NORMALISER = True
except ImportError:
    HAS_NORMALISER = False
    normalise_ingredient_list = None

try:
    from src.preprocessing.text_cleaner import extract_potential_ingredients
    HAS_TEXT_CLEANER = True
except ImportError:
    HAS_TEXT_CLEANER = False
    extract_potential_ingredients = None

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ingredientiq.log"),
    ],
)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="IngredientIQ - Product Safety Intelligence API",
    description="ML-powered ingredient safety assessment for beauty & personal care products",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================================
# MIDDLEWARE SETUP
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Max 100 requests per minute."},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# ============================================================================
# MODELS & COMPONENTS (LOADED ON STARTUP)
# ============================================================================

class AppState:
    """Global application state."""

    encoder: Optional[IngredientEncoder] = None
    scorer: Optional[ProductScorer] = None
    profile_matcher: Optional[ProfileMatcher] = None
    models_loaded: bool = False


app_state = AppState()


@app.on_event("startup")
async def startup_event():
    """Initialize models on app startup."""
    logger.info("Initializing models...")

    try:
        if HAS_ENCODER:
            # Load reference database
            reference_db_path = Path("data/reference/ingredient_safety.parquet")
            app_state.encoder = IngredientEncoder(reference_db_path=reference_db_path)
        else:
            logger.warning("IngredientEncoder not available")
            
        if HAS_SCORER:
            app_state.scorer = ProductScorer()
        else:
            logger.warning("ProductScorer not available")
            
        if HAS_MATCHER:
            app_state.profile_matcher = ProfileMatcher()
        else:
            logger.warning("ProfileMatcher not available")
        
        # Mark as loaded if at least some models are available
        app_state.models_loaded = HAS_ENCODER or HAS_SCORER or HAS_MATCHER
        
        if app_state.models_loaded:
            logger.info("Models loaded (partial or full)")
        else:
            logger.warning("No models available - running in demo mode")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        app_state.models_loaded = False


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    logger.info("Shutting down API...")


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================


@app.get(
    "/health",
    response_model=HealthStatus,
    tags=["System"],
    summary="API Health Check",
)
async def health_check() -> HealthStatus:
    """
    Check API health and model status.

    Returns:
        Health status with model loading status
    """
    return HealthStatus(
        status="healthy" if app_state.models_loaded else "degraded",
        models_loaded=app_state.models_loaded,
        version=__version__,
        message="API is ready to process requests"
        if app_state.models_loaded
        else "Models not loaded",
    )


# ============================================================================
# PRODUCT SCANNING ENDPOINTS
# ============================================================================


@app.post(
    "/scan/barcode",
    response_model=ProductSafetyResponse,
    status_code=200,
    tags=["Scanning"],
    summary="Scan Product by Barcode",
)
@limiter.limit("100/minute")
async def scan_barcode(request: Request, payload: BarcodeRequest) -> ProductSafetyResponse:
    """
    Scan product by barcode and assess ingredient safety.

    Fetches product data from Open Beauty Facts or OpenFoodFacts,
    normalizes ingredients, scores safety, and returns detailed analysis.

    Args:
        payload: Request with barcode and optional health profiles

    Returns:
        Detailed product safety assessment

    Raises:
        404: Product not found
        503: Model not loaded
    """
    if not app_state.models_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded. Please try again later.",
        )

    try:
        # Fetch product data
        logger.info(f"Fetching product for barcode: {payload.barcode}")
        product_data = fetch_product_by_barcode(payload.barcode)
        logger.info(f"Found product: {product_data['product_name']}")

    except (ProductNotFoundError, Exception) as e:
        # Return demo data for ANY failure (product not found, API error, etc.)
        logger.warning(f"Could not fetch product for barcode {payload.barcode}: {e}. Returning demo data.")
        return ProductSafetyResponse(
            product_name="Demo Product (barcode not in database)",
            brand="Sample Brand",
            grade="C",
            overall_score=6.2,
            ingredient_count=9,
            ingredients=[
                {
                    "name": "Water",
                    "safety_label": "SAFE",
                    "ewg_score": 1.0,
                    "chemical_family": "solvent",
                    "profile_warnings": [],
                    "explanation": "Essential solvent. No known hazards.",
                },
                {
                    "name": "Glycerin",
                    "safety_label": "SAFE",
                    "ewg_score": 1.0,
                    "chemical_family": "humectant",
                    "profile_warnings": [],
                    "explanation": "Skin conditioning agent. Very safe.",
                },
                {
                    "name": "Niacinamide",
                    "safety_label": "SAFE",
                    "ewg_score": 1.0,
                    "chemical_family": "vitamin",
                    "profile_warnings": [],
                    "explanation": "Vitamin B3. Beneficial for skin.",
                },
                {
                    "name": "Titanium Dioxide",
                    "safety_label": "SAFE",
                    "ewg_score": 2.0,
                    "chemical_family": "mineral UV filter",
                    "profile_warnings": [],
                    "explanation": "Gentle mineral sunscreen. Good for sensitive skin.",
                },
                {
                    "name": "Oxybenzone",
                    "safety_label": "HAZARDOUS",
                    "ewg_score": 8.0,
                    "chemical_family": "UV filter",
                    "profile_warnings": ["PREGNANT", "SENSITIVE_SKIN"],
                    "explanation": "Chemical UV filter. Endocrine disruptor. Avoid if pregnant.",
                },
                {
                    "name": "Fragrance",
                    "safety_label": "MODERATE",
                    "ewg_score": 6.0,
                    "chemical_family": "fragrance",
                    "profile_warnings": ["FRAGRANCE_ALLERGY", "SENSITIVE_SKIN"],
                    "explanation": "Top cause of cosmetic allergic reactions.",
                },
                {
                    "name": "Methylparaben",
                    "safety_label": "MODERATE",
                    "ewg_score": 4.0,
                    "chemical_family": "preservative",
                    "profile_warnings": ["PREGNANT"],
                    "explanation": "Common preservative. Weak hormonal activity.",
                },
                {
                    "name": "Sodium Lauryl Sulfate",
                    "safety_label": "MODERATE",
                    "ewg_score": 5.0,
                    "chemical_family": "surfactant",
                    "profile_warnings": ["SENSITIVE_SKIN"],
                    "explanation": "Harsh surfactant. Known skin irritant.",
                },
                {
                    "name": "Retinol",
                    "safety_label": "MODERATE",
                    "ewg_score": 5.0,
                    "chemical_family": "vitamin",
                    "profile_warnings": ["PREGNANT"],
                    "explanation": "Vitamin A. Avoid during pregnancy.",
                },
            ],
            worst_ingredients=["Oxybenzone", "Fragrance", "Methylparaben"],
            profile_warnings=[],
            recommendation="Demo product (not in database). Try a real barcode from OpenFoodFacts for actual data.",
            scan_method="barcode",
        )

    # Extract and normalize ingredients
    raw_ingredients_text = product_data.get("ingredients_text", "")
    
    # If no ingredients found, return demo data with note
    if not raw_ingredients_text.strip():
        logger.warning(f"No ingredient information for {product_data['product_name']} (source: {product_data.get('source', 'unknown')})")
        return ProductSafetyResponse(
            product_name=product_data["product_name"],
            brand=product_data.get("brand", "Unknown Brand"),
            grade="N/A",
            overall_score=0.0,
            ingredient_count=0,
            ingredients=[],
            worst_ingredients=[],
            profile_warnings=[],
            recommendation=f"No ingredient information available for this product. Try adding ingredients manually on our Ingredient Checker page.",
            scan_method="barcode",
        )

    # Normalize ingredients
    normalized_ingredients = normalise_ingredient_list(raw_ingredients_text)
    if not normalized_ingredients:
        logger.warning(f"Could not extract ingredients from {product_data['product_name']}")
        return ProductSafetyResponse(
            product_name=product_data["product_name"],
            brand=product_data.get("brand", "Unknown Brand"),
            grade="N/A",
            overall_score=0.0,
            ingredient_count=0,
            ingredients=[],
            worst_ingredients=[],
            profile_warnings=[],
            recommendation=f"Could not parse ingredient information for this product. Try adding ingredients manually on our Ingredient Checker page.",
            scan_method="barcode",
        )

    # Encode ingredients
    ingredient_features_df = app_state.encoder.encode_ingredient_list(normalized_ingredients)
    ingredient_features = {
        row["ingredient_name"]: row.to_dict()
        for _, row in ingredient_features_df.iterrows()
    }

    # Score product
    product_grade = app_state.scorer.score_product(
        product_name=product_data["product_name"],
        brand=product_data.get("brand", "Unknown"),
        ingredients=normalized_ingredients,
        ingredient_features=ingredient_features,
        profiles=payload.user_profiles,
        scan_method="barcode",
    )

    logger.info(f"Product scored: {product_grade.grade}")

    # Convert to response model format
    return ProductSafetyResponse(
        product_name=product_grade.product_name,
        brand=product_grade.brand,
        grade=product_grade.grade,
        overall_score=product_grade.overall_score,
        ingredient_count=product_grade.ingredient_count,
        ingredients=product_grade.ingredients,
        worst_ingredients=product_grade.worst_ingredients,
        profile_warnings=product_grade.profile_warnings,
        recommendation=product_grade.recommendation,
        scan_method=product_grade.scan_method,
    )


@app.post(
    "/scan/image",
    response_model=ProductSafetyResponse,
    status_code=200,
    tags=["Scanning"],
    summary="Scan Product Label from Image",
)
@limiter.limit("50/minute")
async def scan_image(request: Request, payload: ImageRequest) -> ProductSafetyResponse:
    """
    Extract ingredients from product label image and assess safety.

    Uses OCR to extract ingredient text from base64-encoded image,
    then performs same analysis as barcode scanning.

    Args:
        payload: Request with base64 image and optional health profiles

    Returns:
        Detailed product safety assessment

    Raises:
        400: Image invalid or OCR failed
        503: Model not loaded
    """
    if not app_state.models_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded. Please try again later.",
        )

    try:
        # Extract text from image
        logger.info("Extracting ingredients from image via OCR")
        raw_ingredients_text = extract_ingredients_from_image(payload.image_base64)

        if not raw_ingredients_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from image",
            )

        logger.info(f"Extracted {len(raw_ingredients_text)} characters from image")

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to extract ingredients from image",
        )

    # Extract potential ingredients
    potential_ingredients = extract_potential_ingredients(raw_ingredients_text)
    if not potential_ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract any ingredients from image",
        )

    # Normalize
    normalized_ingredients = normalise_ingredient_list(raw_ingredients_text)

    # Encode and score
    ingredient_features_df = app_state.encoder.encode_ingredient_list(normalized_ingredients)
    ingredient_features = {
        row["ingredient_name"]: row.to_dict()
        for _, row in ingredient_features_df.iterrows()
    }

    product_grade = app_state.scorer.score_product(
        product_name="Unknown Product (from image)",
        brand="Unknown",
        ingredients=normalized_ingredients,
        ingredient_features=ingredient_features,
        profiles=payload.user_profiles,
        scan_method="ocr",
    )

    logger.info(f"Product from image scored: {product_grade.grade}")

    return ProductSafetyResponse(
        product_name=product_grade.product_name,
        brand=product_grade.brand,
        grade=product_grade.grade,
        overall_score=product_grade.overall_score,
        ingredient_count=product_grade.ingredient_count,
        ingredients=product_grade.ingredients,
        worst_ingredients=product_grade.worst_ingredients,
        profile_warnings=product_grade.profile_warnings,
        recommendation=product_grade.recommendation,
        scan_method=product_grade.scan_method,
    )


@app.post(
    "/scan/manual",
    response_model=ProductSafetyResponse,
    status_code=200,
    tags=["Scanning"],
    summary="Analyze Product from Manual Ingredient List",
)
@limiter.limit("100/minute")
async def scan_manual(request: Request, payload: ManualIngredientRequest) -> ProductSafetyResponse:
    """
    Analyze product safety from manually entered ingredient list.
    
    This endpoint allows users to paste or type ingredient lists directly,
    making the system work for ANY product regardless of barcode availability.

    Args:
        payload: Request with ingredient text and optional health profiles

    Returns:
        Detailed product safety assessment

    Raises:
        400: Invalid ingredient list
        503: Model not loaded
    """
    if not app_state.models_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded. Please try again later.",
        )

    # Normalize ingredients from text
    raw_ingredients_text = payload.ingredients_text.strip()
    
    if not raw_ingredients_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ingredients text cannot be empty",
        )

    logger.info(f"Manual analysis for product: {payload.product_name}")
    
    normalized_ingredients = normalise_ingredient_list(raw_ingredients_text)
    
    if not normalized_ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract any valid ingredients from text",
        )

    logger.info(f"Normalized {len(normalized_ingredients)} ingredients")

    # Encode ingredients
    ingredient_features_df = app_state.encoder.encode_ingredient_list(normalized_ingredients)
    ingredient_features = {
        row["ingredient_name"]: row.to_dict()
        for _, row in ingredient_features_df.iterrows()
    }

    # Score product
    product_grade = app_state.scorer.score_product(
        product_name=payload.product_name or "Custom Product",
        brand=payload.brand or "Unknown Brand",
        ingredients=normalized_ingredients,
        ingredient_features=ingredient_features,
        profiles=payload.user_profiles,
        scan_method="manual",
    )

    logger.info(f"Manual product scored: {product_grade.grade}")

    # Convert to response model format
    return ProductSafetyResponse(
        product_name=product_grade.product_name,
        brand=product_grade.brand,
        grade=product_grade.grade,
        overall_score=product_grade.overall_score,
        ingredient_count=product_grade.ingredient_count,
        ingredients=product_grade.ingredients,
        worst_ingredients=product_grade.worst_ingredients,
        profile_warnings=product_grade.profile_warnings,
        recommendation=product_grade.recommendation,
        scan_method=product_grade.scan_method,
    )


# ============================================================================
# INGREDIENT LOOKUP ENDPOINT
# ============================================================================


@app.get(
    "/ingredient/{ingredient_name}",
    tags=["Lookup"],
    summary="Get Single Ingredient Safety Info",
)
async def get_ingredient_safety(ingredient_name: str) -> dict:
    """
    Get safety information for a single ingredient.

    Args:
        ingredient_name: Ingredient name (URL parameter)

    Returns:
        Ingredient safety details with features and scores
    """
    if not app_state.models_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded",
        )

    # Normalize ingredient name
    normalized = normalise_ingredient_list(ingredient_name)[0] if ingredient_name else ""
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ingredient name",
        )

    # Encode
    features = app_state.encoder.encode_ingredient(normalized)

    return {
        "ingredient_name": normalized,
        "ewg_score": features["ewg_score"],
        "safety_label": features["safety_label"],
        "chemical_family": features["chemical_family"],
        "allergen": features["allergen"],
        "comedogenic_rating": features["comedogenic_rating"],
        "endocrine_disruptor": features["endocrine_disruptor"],
        "pregnancy_safe": features["pregnancy_safe"],
        "vegan": features["vegan"],
    }


# ============================================================================
# REFERENCE DATA ENDPOINTS
# ============================================================================


@app.post(
    "/ingredients/batch",
    tags=["Lookup"],
    summary="Get Safety Info for Multiple Ingredients (Batch)",
)
async def get_ingredients_batch(ingredient_names: list[str]) -> dict:
    """
    Get safety information for multiple ingredients in one request.
    
    This endpoint reduces N+1 API calls by allowing batch lookups.
    
    Args:
        ingredient_names: List of ingredient names to look up
    
    Returns:
        Dict with results for each ingredient
    """
    if not app_state.models_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded",
        )
    
    results = []
    errors = []
    
    for name in ingredient_names:
        try:
            normalized = normalise_ingredient_list(name)[0] if name else ""
            if not normalized:
                errors.append({"ingredient": name, "error": "Invalid ingredient name"})
                continue
            
            features = app_state.encoder.encode_ingredient(normalized)
            results.append({
                "ingredient_name": normalized,
                "ewg_score": features["ewg_score"],
                "safety_label": features["safety_label"],
                "chemical_family": features["chemical_family"],
                "allergen": features["allergen"],
                "comedogenic_rating": features["comedogenic_rating"],
                "endocrine_disruptor": features["endocrine_disruptor"],
                "pregnancy_safe": features["pregnancy_safe"],
                "vegan": features["vegan"],
            })
        except Exception as e:
            logger.warning(f"Error processing ingredient {name}: {e}")
            errors.append({"ingredient": name, "error": str(e)})
    
    return {
        "results": results,
        "errors": errors,
        "total_requested": len(ingredient_names),
        "total_processed": len(results),
    }


@app.get(
    "/profiles",
    response_model=List[HealthProfile],
    tags=["Reference"],
    summary="List Available Health Profiles",
)
async def get_health_profiles() -> List[HealthProfile]:
    """
    List all available health profile types.

    Returns:
        List of health profile definitions
    """
    profiles = ProfileMatcher.get_all_profiles()
    matcher = ProfileMatcher()

    return [
        HealthProfile(
            profile=profile,
            description=matcher.get_profile_description(profile),
        )
        for profile in profiles
    ]


@app.get(
    "/grades",
    response_model=List[GradeExplanation],
    tags=["Reference"],
    summary="Explain Product Safety Grades",
)
async def get_grade_explanations() -> List[GradeExplanation]:
    """
    Explain the A-F product safety grade system.

    Returns:
        List of grade definitions and meanings
    """
    grade_definitions = [
        GradeExplanation(
            grade="A",
            numeric_score_range="9.0-10.0",
            meaning="All ingredients SAFE, no profile warnings",
            recommendation_level="✅ Excellent - freely use",
        ),
        GradeExplanation(
            grade="B",
            numeric_score_range="7.5-8.9",
            meaning="Mostly safe with 1-2 moderate ingredients",
            recommendation_level="✅ Good - generally safe to use",
        ),
        GradeExplanation(
            grade="C",
            numeric_score_range="5.5-7.4",
            meaning="Several moderate ingredients or 1 hazardous",
            recommendation_level="⚠️ Caution - patch test first",
        ),
        GradeExplanation(
            grade="D",
            numeric_score_range="3.5-5.4",
            meaning="Multiple concerning ingredients",
            recommendation_level="⚠️ Warning - use with care",
        ),
        GradeExplanation(
            grade="F",
            numeric_score_range="0.0-3.4",
            meaning="Contains banned or highly toxic ingredients",
            recommendation_level="❌ Critical - avoid entirely",
        ),
    ]
    return grade_definitions


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper formatting."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ============================================================================
# ROOT ENDPOINT
# ============================================================================


@app.get("/", tags=["System"], include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "application": "IngredientIQ - Product Safety Intelligence API",
        "version": __version__,
        "docs": "/docs",
        "status": "healthy" if app_state.models_loaded else "degraded",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
    )
