"""Tests for ML safety classifier module."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from src.models.safety_classifier import SafetyClassifier


class TestSafetyClassifier:
    """Test cases for SafetyClassifier."""

    @pytest.fixture
    def sample_data(self):
        """Create sample training data."""
        np.random.seed(42)
        X = pd.DataFrame({
            "ewg_score": np.random.uniform(0, 10, 100),
            "allergen": np.random.choice([0, 1], 100),
            "comedogenic_rating": np.random.uniform(0, 5, 100),
            "endocrine_disruptor": np.random.choice([0, 1], 100),
        })
        # Create labels based on simple rules
        y = pd.Series([
            2 if row["ewg_score"] > 7 else (1 if row["ewg_score"] > 4 else 0)
            for _, row in X.iterrows()
        ])
        return X, y

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return SafetyClassifier(model_type="xgboost")

    def test_classifier_initialization(self, classifier):
        """Test classifier is initialized correctly."""
        assert classifier.model_type == "xgboost"
        assert classifier.model is None
        assert classifier.models_loaded is False

    def test_model_training(self, classifier, sample_data):
        """Test model training completes successfully."""
        X, y = sample_data
        metrics = classifier.train(X, y)
        
        assert classifier.model is not None
        assert "accuracy" in metrics
        assert "confusion_matrix" in metrics
        assert metrics["accuracy"] >= 0 and metrics["accuracy"] <= 1

    def test_prediction_after_training(self, classifier, sample_data):
        """Test predictions work after training."""
        X, y = sample_data
        classifier.train(X, y, test_size=0.2)
        
        # Make predictions on subset of training data
        predictions = classifier.predict(X.iloc[:10])
        assert len(predictions) == 10
        assert all(pred in ["SAFE", "MODERATE", "HAZARDOUS", "UNKNOWN"] for pred in predictions)

    def test_predict_proba(self, classifier, sample_data):
        """Test probability predictions."""
        X, y = sample_data
        classifier.train(X, y, test_size=0.2)
        
        proba = classifier.predict_proba(X.iloc[:5])
        assert len(proba) == 5
        
        # Each probability dict should contain all labels
        for prob_dict in proba:
            assert "SAFE" in prob_dict
            assert "MODERATE" in prob_dict
            assert "HAZARDOUS" in prob_dict
            
            # Probabilities should sum to ~1.0
            total = sum(prob_dict.values())
            assert 0.9 < total < 1.1

    def test_model_save_and_load(self, classifier, sample_data, tmp_path):
        """Test model can be saved and loaded."""
        X, y = sample_data
        classifier.train(X, y, test_size=0.2)
        
        # Save model
        model_path = tmp_path / "test_model.pkl"
        classifier.save(model_path)
        assert model_path.exists()
        
        # Load model
        new_classifier = SafetyClassifier()
        new_classifier.load(model_path)
        
        # Loaded model should make same predictions
        original_predictions = classifier.predict(X.iloc[:5])
        loaded_predictions = new_classifier.predict(X.iloc[:5])
        assert original_predictions == loaded_predictions

    def test_feature_importance(self, classifier, sample_data):
        """Test feature importance extraction."""
        X, y = sample_data
        classifier.train(X, y, test_size=0.2)
        
        importance = classifier.feature_importance()
        assert isinstance(importance, dict)
        assert "ewg_score" in importance
        assert all(imp >= 0 for imp in importance.values())

    def test_predict_before_training_raises_error(self, classifier):
        """Test that predicting before training raises error."""
        X = pd.DataFrame({"ewg_score": [5.0]})
        with pytest.raises(ValueError):
            classifier.predict(X)

    def test_label_to_idx_mapping(self):
        """Test label to index mapping is correct."""
        from src.models.safety_classifier import LABEL_TO_IDX
        assert LABEL_TO_IDX["SAFE"] == 0
        assert LABEL_TO_IDX["MODERATE"] == 1
        assert LABEL_TO_IDX["HAZARDOUS"] == 2

    def test_different_model_types(self, sample_data):
        """Test both model types can be initialized and trained."""
        X, y = sample_data
        
        for model_type in ["xgboost", "randomforest"]:
            classifier = SafetyClassifier(model_type=model_type)
            metrics = classifier.train(X, y, test_size=0.2)
            assert classifier.model is not None
            assert metrics["accuracy"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
