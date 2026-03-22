"""Barcode product data fetcher from OpenBeautyFacts and OpenFoodFacts APIs."""

import logging
import time
from functools import lru_cache
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class ProductNotFoundError(Exception):
    """Raised when a product cannot be found in any database."""

    pass


class BarcodeAPIError(Exception):
    """Raised when API request fails with a non-404 error."""

    pass


@lru_cache(maxsize=512)
def fetch_product_by_barcode(barcode: str) -> Dict[str, Any]:
    """
    Fetch product data from Open Beauty Facts or OpenFoodFacts API.

    Attempts to fetch from Open Beauty Facts first (cosmetics/beauty products),
    then falls back to OpenFoodFacts (food products). Returns structured
    product data with ingredients, brand, and metadata.

    Args:
        barcode: Product barcode as string (EAN-13, EAN-8, UPC-A, etc)

    Returns:
        Dictionary containing:
            - product_name: str
            - brand: str, optional
            - ingredients_text: str, optional
            - image_url: str, optional
            - categories: List[str], optional
            - labels: List[str], optional
            - barcode: str
            - source: str (openbeautyfacts|openfoodfacts)

    Raises:
        ProductNotFoundError: If product not found in both databases
        BarcodeAPIError: If API request fails with non-404 error
    """
    start_time = time.time()

    # Try Open Beauty Facts first
    try:
        logger.info(f"Fetching product from OpenBeautyFacts for barcode: {barcode}")
        product_data = _fetch_from_openbeautyfacts(barcode)
        elapsed_time = time.time() - start_time
        logger.info(
            f"Successfully fetched from OpenBeautyFacts in {elapsed_time:.2f}s"
        )
        return product_data
    except ProductNotFoundError:
        logger.debug(f"Product not found in OpenBeautyFacts, trying OpenFoodFacts")
    except BarcodeAPIError as e:
        logger.warning(f"OpenBeautyFacts API error: {e}, trying OpenFoodFacts")

    # Fall back to OpenFoodFacts
    try:
        logger.info(f"Fetching product from OpenFoodFacts for barcode: {barcode}")
        product_data = _fetch_from_openfoodfacts(barcode)
        elapsed_time = time.time() - start_time
        logger.info(
            f"Successfully fetched from OpenFoodFacts in {elapsed_time:.2f}s"
        )
        return product_data
    except ProductNotFoundError:
        logger.debug(f"Product not found in OpenFoodFacts, trying EAN-Search")
    except BarcodeAPIError as e:
        logger.warning(f"OpenFoodFacts API error: {e}, trying EAN-Search")

    # Fall back to EAN-Search
    try:
        logger.info(f"Fetching product from EAN-Search for barcode: {barcode}")
        product_data = _fetch_from_ean_search(barcode)
        elapsed_time = time.time() - start_time
        logger.info(
            f"Successfully fetched from EAN-Search in {elapsed_time:.2f}s"
        )
        return product_data
    except ProductNotFoundError:
        logger.error(f"Product not found in any database for barcode: {barcode}")
        raise ProductNotFoundError(
            f"Product with barcode {barcode} not found in OpenBeautyFacts, OpenFoodFacts, or EAN-Search"
        )
    except BarcodeAPIError as e:
        logger.error(f"EAN-Search API error: {e}")
        raise BarcodeAPIError(f"Failed to fetch from EAN-Search: {e}")


def _fetch_from_openbeautyfacts(barcode: str) -> Dict[str, Any]:
    """
    Fetch product data from OpenBeautyFacts API.

    Args:
        barcode: Product barcode

    Returns:
        Structured product dictionary

    Raises:
        ProductNotFoundError: If product returns 404
        BarcodeAPIError: If API request fails
    """
    url = f"https://world.openbeautyfacts.org/api/v2/product/{barcode}"
    headers = {"User-Agent": "IngredientIQ/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ProductNotFoundError(f"Product {barcode} not found")
        raise BarcodeAPIError(f"HTTP {response.status_code}: {e}")
    except requests.exceptions.RequestException as e:
        raise BarcodeAPIError(f"Request failed: {e}")

    data = response.json()

    if data.get("status") == 0:
        raise ProductNotFoundError(f"Product {barcode} not found (status=0)")

    product = data.get("product", {})
    return {
        "product_name": product.get("name", "Unknown Product"),
        "brand": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_front_url", ""),
        "categories": product.get("categories_tags", []),
        "labels": product.get("labels_tags", []),
        "barcode": barcode,
        "source": "openbeautyfacts",
    }


def _fetch_from_openfoodfacts(barcode: str) -> Dict[str, Any]:
    """
    Fetch product data from OpenFoodFacts API.

    Args:
        barcode: Product barcode

    Returns:
        Structured product dictionary

    Raises:
        ProductNotFoundError: If product returns 404
        BarcodeAPIError: If API request fails
    """
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}"
    headers = {"User-Agent": "IngredientIQ/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ProductNotFoundError(f"Product {barcode} not found")
        raise BarcodeAPIError(f"HTTP {response.status_code}: {e}")
    except requests.exceptions.RequestException as e:
        raise BarcodeAPIError(f"Request failed: {e}")

    data = response.json()

    if data.get("status") == 0:
        raise ProductNotFoundError(f"Product {barcode} not found (status=0)")

    product = data.get("product", {})
    return {
        "product_name": product.get("product_name", "Unknown Product"),
        "brand": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "image_url": product.get("image_front_url", ""),
        "categories": product.get("categories_tags", []),
        "labels": product.get("labels_tags", []),
        "barcode": barcode,
        "source": "openfoodfacts",
    }


def _fetch_from_ean_search(barcode: str) -> Dict[str, Any]:
    """
    Fetch product data from EAN-Search API.
    
    This is a fallback data source that provides product names and categories
    for barcodes not found in OpenBeautyFacts or OpenFoodFacts.

    Args:
        barcode: Product barcode

    Returns:
        Structured product dictionary

    Raises:
        ProductNotFoundError: If product returns empty result
        BarcodeAPIError: If API request fails
    """
    url = f"https://www.ean-search.org/api/1/json"
    params = {
        "barcode": barcode,
        "op": "barcode-lookup"
    }
    headers = {"User-Agent": "IngredientIQ/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ProductNotFoundError(f"Product {barcode} not found on EAN-Search")
        raise BarcodeAPIError(f"EAN-Search HTTP {response.status_code}: {e}")
    except requests.exceptions.RequestException as e:
        raise BarcodeAPIError(f"EAN-Search request failed: {e}")

    data = response.json()

    # Check if product was found (status=0 means success, status!=0 means not found)
    if data.get("status") != 0 or not data.get("product"):
        raise ProductNotFoundError(f"Product {barcode} not found on EAN-Search")

    product = data.get("product", {})
    
    return {
        "product_name": product.get("title", "Unknown Product"),
        "brand": product.get("brand", ""),
        "ingredients_text": "",  # EAN-Search doesn't provide ingredients
        "image_url": product.get("image", ""),
        "categories": [product.get("category", "")],
        "labels": [],
        "barcode": barcode,
        "source": "ean-search",
    }
