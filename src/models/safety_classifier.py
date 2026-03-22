"""ML Safety Classifier for ingredient hazard assessment."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

# Safety label hierarchy
SAFETY_LABELS = ["SAFE", "MODERATE", "HAZARDOUS", "UNKNOWN"]
LABEL_TO_IDX = {label: idx for idx, label in enumerate(SAFETY_LABELS)}
IDX_TO_LABEL = {idx: label for label, idx in LABEL_TO_IDX.items()}


class SafetyClassifier:
    """Classifier for ingredient safety assessment using ML."""

    def __init__(self, model_type: str = "xgboost") -> None:
        """
        Initialize classifier with specified model type.

        Args:
            model_type: "xgboost" or "randomforest"
        """
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.label_map = LABEL_TO_IDX
        logger.info(f"Initialized SafetyClassifier with model_type: {model_type}")

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        seed: int = 42,
    ) -> dict:
        """
        Train safety classifier on ingredient features.

        Features expected:
        - ewg_score: float (0-10)
        - allergen: bool
        - comedogenic_rating: float (0-5)
        - endocrine_disruptor: bool

        Target variable should be numeric (0=SAFE, 1=MODERATE, 2=HAZARDOUS).

        Args:
            X: Feature DataFrame
            y: Target Series with safety labels
            test_size: Fraction for test split
            seed: Random seed for reproducibility

        Returns:
            Dictionary with training metrics:
                - accuracy: overall accuracy
                - precision: weighted precision
                - recall: weighted recall
                - confusion_matrix: confusion matrix
                - classification_report: detailed metrics per class
        """
        from sklearn.model_selection import train_test_split

        # Convert labels to indices if necessary
        if y.dtype == "object":
            y = y.map(self.label_map)

        # Store feature names
        self.feature_names = X.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=seed, stratify=y
        )

        # Initialize and train model
        if self.model_type == "xgboost":
            self.model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=seed,
                verbosity=0,
            )
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=seed,
                n_jobs=-1,
            )

        self.model.fit(X_train, y_train)
        logger.info(f"Model trained on {len(X_train)} samples")

        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)

        metrics = {
            "accuracy": float(self.model.score(X_test, y_test)),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
        }

        # Log metrics
        logger.info(f"Model accuracy: {metrics['accuracy']:.4f}")
        logger.debug(f"Classification report:\n{classification_report(y_test, y_pred)}")

        return metrics

    def predict(self, X: pd.DataFrame) -> List[str]:
        """
        Predict safety labels for ingredients.

        Args:
            X: Feature DataFrame with required columns

        Returns:
            List of safety label strings per ingredient
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        predictions = self.model.predict(X)
        labels = [IDX_TO_LABEL.get(pred, "UNKNOWN") for pred in predictions]
        return labels

    def predict_proba(self, X: pd.DataFrame) -> List[dict]:
        """
        Predict safety labels with confidence scores.

        Args:
            X: Feature DataFrame

        Returns:
            List of dicts with label -> probability mappings
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        proba = self.model.predict_proba(X)
        results = []

        for prob_row in proba:
            label_probs = {}
            for idx, prob in enumerate(prob_row):
                label = IDX_TO_LABEL.get(idx, "UNKNOWN")
                label_probs[label] = float(prob)
            results.append(label_probs)

        return results

    def save(self, path: Path) -> None:
        """
        Save trained model to disk.

        Args:
            path: Path to save model (.pkl file)
        """
        if self.model is None:
            raise ValueError("No model to save. Train first.")

        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "feature_names": self.feature_names,
                "model_type": self.model_type,
            },
            path,
        )
        logger.info(f"Model saved to {path}")

    def load(self, path: Path) -> None:
        """
        Load trained model from disk.

        Args:
            path: Path to saved model (.pkl file)
        """
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        data = joblib.load(path)
        self.model = data["model"]
        self.feature_names = data.get("feature_names")
        self.model_type = data.get("model_type", "unknown")
        logger.info(f"Model loaded from {path}")

    def feature_importance(self) -> dict:
        """
        Get feature importance scores from trained model.

        Returns:
            Dictionary mapping feature names to importance values
        """
        if self.model is None or self.feature_names is None:
            return {}

        if hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            return dict(zip(self.feature_names, importances))

        return {}
