"""End-to-end ML training pipeline."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src.features.ingredient_encoder import IngredientEncoder
from src.models.safety_classifier import SafetyClassifier

logger = logging.getLogger(__name__)


def create_synthetic_training_data(n_samples: int = 500) -> tuple:
    """
    Create synthetic training data for the safety classifier.

    In production, this would load real labeled ingredient data from a database.

    Args:
        n_samples: Number of samples to generate

    Returns:
        Tuple of (X_train, y_train) DataFrames
    """
    logger.info(f"Generating synthetic training data ({n_samples} samples)...")

    np.random.seed(42)

    # Generate features
    X_data = {
        "ewg_score": np.random.uniform(0, 10, n_samples),
        "allergen": np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        "comedogenic_rating": np.random.uniform(0, 5, n_samples),
        "endocrine_disruptor": np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
    }

    # Generate labels based on rules
    y_data = []
    for i in range(n_samples):
        ewg = X_data["ewg_score"][i]
        allergen = X_data["allergen"][i]
        hazard = X_data["endocrine_disruptor"][i]

        # Simple rule-based label generation
        if ewg >= 7 and hazard:
            label = 2  # HAZARDOUS
        elif ewg >= 5 or (allergen and ewg >= 3):
            label = 1  # MODERATE
        else:
            label = 0  # SAFE

        y_data.append(label)

    X = pd.DataFrame(X_data)
    y = pd.Series(y_data, name="safety_label")

    logger.info(f"Training data shape: X {X.shape}, y {y.shape}")
    logger.info(f"Label distribution:\n{y.value_counts().sort_index()}")

    return X, y


def train_classifier(X: pd.DataFrame, y: pd.Series, model_dir: Path) -> str:
    """
    Train safety classifier on labeled ingredient data.

    Args:
        X: Feature DataFrame
        y: Target Series (with SAFE, MODERATE, HAZARDOUS labels)
        model_dir: Directory to save trained model

    Returns:
        Path to saved model file
    """
    logger.info("Training safety classifier...")
    model_dir.mkdir(parents=True, exist_ok=True)

    # Initialize and train classifier
    classifier = SafetyClassifier(model_type="xgboost")
    metrics = classifier.train(X, y, test_size=0.2, seed=42)

    # Log metrics
    logger.info(f"Training complete!")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"  Confusion matrix:\n{metrics['confusion_matrix']}")

    # Save model
    model_path = model_dir / "safety_classifier.pkl"
    classifier.save(model_path)
    logger.info(f"✅ Model saved to {model_path}")

    return str(model_path)


def main(project_dir: Path) -> dict:
    """
    Execute complete training pipeline.

    Steps:
    1. Create or load training data
    2. Train classifier
    3. Verify all model files exist
    4. Return summary

    Args:
        project_dir: Root project directory

    Returns:
        Summary dictionary with completion status
    """
    logger.info("=" * 70)
    logger.info("INGREDIENTIQ TRAINING PIPELINE")
    logger.info("=" * 70)

    model_dir = project_dir / "models"
    data_dir = project_dir / "data"

    # Create synthetic training data
    X_train, y_train = create_synthetic_training_data(n_samples=500)

    # Train classifier
    model_path = train_classifier(X_train, y_train, model_dir)

    # Verify model files
    required_files = [
        model_dir / "safety_classifier.pkl",
        data_dir / "reference" / "ingredient_safety.parquet",
        data_dir / "reference" / "inci_synonyms.parquet",
    ]

    logger.info("\nVerifying model files...")
    missing_files = []
    for file_path in required_files:
        if file_path.exists():
            logger.info(f"  ✅ {file_path.name}")
        else:
            logger.warning(f"  ❌ {file_path.name} (will be created on first use)")
            missing_files.append(str(file_path))

    # Summary
    summary = {
        "status": "completed",
        "classifier_trained": True,
        "classifier_path": str(model_path),
        "training_samples": len(X_train),
        "missing_files": missing_files,
    }

    logger.info("\n" + "=" * 70)
    logger.info("TRAINING PIPELINE SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Status: {summary['status']}")
    logger.info(f"Classifier trained: {summary['classifier_trained']}")
    logger.info(f"Training samples: {summary['training_samples']}")

    if missing_files:
        logger.warning(f"Missing {len(missing_files)} expected files (will be created on startup)")

    logger.info("=" * 70)

    return summary


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    main(project_dir)
