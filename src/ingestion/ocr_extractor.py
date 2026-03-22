"""OCR-based ingredient extraction from product label images."""

import base64
import io
import logging
import re
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Common OCR errors and corrections
OCR_CORRECTIONS = {
    r"\bi\b": "l",  # i -> l
    r"\bl\b": "1",  # single l -> 1 (context-dependent)
    r"\bcl\b": "cl",  # cl -> cl
    r"\brn\b": "m",  # rn -> m
    r"\bO\b": "0",  # O -> 0
    r"\bS\b": "5",  # S -> 5
    r"\bZ\b": "2",  # Z -> 2
}


def extract_ingredients_from_image(
    image_source: Union[str, Path],
) -> str:
    """
    Extract ingredient text from product label image using OCR.

    Accepts file path or base64-encoded image string. Preprocesses image
    (grayscale, denoise, threshold, deskew) for optimal OCR accuracy.
    Post-processes extracted text to fix common OCR errors.

    Args:
        image_source: File path (str or Path) or base64-encoded image string

    Returns:
        Cleaned raw ingredient string

    Raises:
        FileNotFoundError: If image file not found
        ValueError: If image source is invalid or not readable
    """
    logger.info(f"Extracting ingredients from image: {image_source}")

    try:
        # Load image
        image = _load_image(image_source)

        # Preprocess image
        processed = _preprocess_image(image)

        # Extract text with pytesseract
        raw_text = pytesseract.image_to_string(processed, config="--psm 6")

        # Post-process text
        cleaned_text = _post_process_text(raw_text)

        logger.info(f"Successfully extracted {len(cleaned_text)} characters")
        return cleaned_text

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise


def _load_image(image_source: Union[str, Path]) -> np.ndarray:
    """
    Load image from file path or base64 string.

    Args:
        image_source: File path or base64 string

    Returns:
        Image as numpy array

    Raises:
        FileNotFoundError: If file not found
        ValueError: If image cannot be read
    """
    if isinstance(image_source, (str, Path)):
        # Check if it's a base64 string (contains only b64 chars)
        if isinstance(image_source, str) and len(image_source) > 100:
            try:
                if all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in image_source[:50]):
                    image_data = base64.b64decode(image_source)
                    image = Image.open(io.BytesIO(image_data))
                    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            except Exception:
                pass

        # Treat as file path
        path = Path(image_source)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")

        image = cv2.imread(str(path))
        if image is None:
            raise ValueError(f"Cannot read image file: {path}")
        return image

    raise ValueError("image_source must be a file path or base64 string")


def _preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Preprocess image for optimal OCR accuracy.

    Steps:
    1. Convert to grayscale
    2. Denoise using bilateral filter
    3. Apply threshold for binarization
    4. Deskew if needed
    5. Resize if too small

    Args:
        image: Input image as numpy array

    Returns:
        Preprocessed image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # Threshold
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Upscale if image is small
    if thresh.shape[0] < 200 or thresh.shape[1] < 200:
        scale_factor = max(200 / thresh.shape[0], 200 / thresh.shape[1])
        thresh = cv2.resize(
            thresh,
            None,
            fx=scale_factor,
            fy=scale_factor,
            interpolation=cv2.INTER_CUBIC,
        )

    # Deskew
    deskewed = _deskew_image(thresh)

    return deskewed


def _deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Deskew image using Hough transform.

    Args:
        image: Binary image

    Returns:
        Deskewed image
    """
    coords = np.column_stack(np.where(image > 0))
    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(coords)[2]

    if -45 > angle > -90:
        angle = 90 + angle

    if angle != 0:
        h, w = image.shape
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        image = cv2.warpAffine(
            image,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

    return image


def _post_process_text(text: str) -> str:
    """
    Post-process OCR text to remove errors and artifacts.

    Steps:
    1. Remove special characters and symbols
    2. Fix common OCR errors
    3. Remove extra whitespace
    4. Lowercase
    5. Remove percentages and numbers in wrong positions

    Args:
        text: Raw OCR output

    Returns:
        Cleaned text
    """
    # Remove special characters (keep alphanumeric, commas, parentheses)
    text = re.sub(r"[^a-zA-Z0-9\s,()%\-]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove percentages at start of words
    text = re.sub(r"\s(\d+%)\s", " ", text)

    # Remove trademark and copyright symbols
    text = re.sub(r"®|©|™", "", text)

    # Fix common OCR errors
    for error_pattern, correction in OCR_CORRECTIONS.items():
        text = re.sub(error_pattern, correction, text)

    # Remove "may contain" phrases and parenthetical claims
    text = re.sub(r"may contain.*?(?=,|$)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\([^)]*may contain[^)]*\)", "", text, flags=re.IGNORECASE)

    # Clean up extra spaces again
    text = re.sub(r"\s+", " ", text).strip()

    return text
