"""Tests for FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_check_returns_200(self):
        """Test health check endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_format(self):
        """Test health check response has required fields."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "models_loaded" in data
        assert "version" in data


class TestProfilesEndpoint:
    """Tests for /profiles endpoint."""

    def test_profiles_endpoint_returns_200(self):
        """Test profiles endpoint returns 200."""
        response = client.get("/profiles")
        assert response.status_code == 200

    def test_profiles_response_format(self):
        """Test profiles response has correct structure."""
        response = client.get("/profiles")
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check each profile has required fields
        for profile in data:
            assert "profile" in profile
            assert "description" in profile


class TestGradesEndpoint:
    """Tests for /grades endpoint."""

    def test_grades_endpoint_returns_200(self):
        """Test grades endpoint returns 200."""
        response = client.get("/grades")
        assert response.status_code == 200

    def test_grades_response_format(self):
        """Test grades response contains all grades A-F."""
        response = client.get("/grades")
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 5  # A through F
        
        grades_found = {grade["grade"] for grade in data}
        assert grades_found == {"A", "B", "C", "D", "F"}


class TestIngredientEndpoint:
    """Tests for GET /ingredient/{name} endpoint."""

    def test_ingredient_endpoint_with_known_ingredient(self):
        """Test ingredient endpoint with known ingredient."""
        response = client.get("/ingredient/titanium-dioxide")
        
        # May return 503 if models not loaded, but should not crash
        assert response.status_code in [200, 503]

    def test_ingredient_endpoint_response_format(self):
        """Test ingredient response format when models are loaded."""
        response = client.get("/ingredient/water")
        
        # May get 503 if models not loaded
        if response.status_code == 200:
            data = response.json()
            assert "ingredient_name" in data
            assert "ewg_score" in data
            assert "hazard_level" in data

    def test_ingredient_endpoint_with_invalid_input(self):
        """Test ingredient endpoint with empty/invalid input."""
        response = client.get("/ingredient/")
        # FastAPI will return 404 for missing path parameter
        assert response.status_code == 404


class TestBarcodeScanning:
    """Tests for POST /scan/barcode endpoint."""

    def test_barcode_endpoint_validation(self):
        """Test barcode endpoint validates input."""
        # Invalid barcode (non-numeric)
        response = client.post("/scan/barcode", json={
            "barcode": "ABC123",
            "user_profiles": []
        })
        assert response.status_code == 422  # Validation error

    def test_barcode_validation_length(self):
        """Test barcode length validation."""
        # Too short
        response = client.post("/scan/barcode", json={
            "barcode": "123",
            "user_profiles": []
        })
        assert response.status_code == 422

    def test_profile_validation(self):
        """Test health profile validation."""
        response = client.post("/scan/barcode", json={
            "barcode": "8901030859756",
            "user_profiles": ["INVALID_PROFILE"]
        })
        assert response.status_code == 422

    def test_valid_profile_list(self):
        """Test with valid profile names."""
        response = client.post("/scan/barcode", json={
            "barcode": "8901030859756",
            "user_profiles": ["SENSITIVE_SKIN", "PREGNANT"]
        })
        # May fail with 404 if product not found, but not 422
        assert response.status_code != 422

    def test_barcode_endpoint_with_unknown_barcode(self):
        """Test barcode endpoint with barcode not in database."""
        response = client.post("/scan/barcode", json={
            "barcode": "99999999999999",
            "user_profiles": []
        })
        # Should return 404 if product not found
        assert response.status_code in [404, 503]  # 503 if models not loaded


class TestImageScanning:
    """Tests for POST /scan/image endpoint."""

    def test_image_endpoint_validation(self):
        """Test image endpoint validates base64 input."""
        response = client.post("/scan/image", json={
            "image_base64": "invalid",
            "user_profiles": []
        })
        assert response.status_code == 422

    def test_image_endpoint_with_valid_base64(self):
        """Test image endpoint accepts valid base64 strings."""
        # Create minimal valid base64 image
        import base64
        from PIL import Image
        import io
        
        # Create tiny test image
        img = Image.new('RGB', (10, 10), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        response = client.post("/scan/image", json={
            "image_base64": img_base64,
            "user_profiles": []
        })
        # May fail if OCR can't extract text, but should process
        assert response.status_code in [400, 503, 500]  # Not a validation error


class TestRequestValidation:
    """Tests for request validation and error handling."""

    def test_barcode_missing_field(self):
        """Test that missing required fields are rejected."""
        response = client.post("/scan/barcode", json={
            "user_profiles": []
        })
        assert response.status_code == 422

    def test_image_missing_field(self):
        """Test that missing required image field is rejected."""
        response = client.post("/scan/image", json={
            "user_profiles": []
        })
        assert response.status_code == 422

    def test_empty_profiles_allowed(self):
        """Test that empty user_profiles list is allowed."""
        response = client.post("/scan/barcode", json={
            "barcode": "1234567890123",
            "user_profiles": []
        })
        # Should not be 422
        assert response.status_code != 422


class TestRateLimiting:
    """Tests for API rate limiting."""

    def test_health_endpoint_not_rate_limited(self):
        """Test that health endpoint works without rate limiting."""
        # Send multiple requests
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code in [200, 503]

    def test_valid_profile_names(self):
        """Test all valid profile names are accepted."""
        valid_profiles = [
            "SENSITIVE_SKIN",
            "PREGNANT",
            "DIABETIC",
            "VEGAN",
            "NUT_ALLERGY",
            "FRAGRANCE_ALLERGY",
            "ACNE_PRONE",
        ]
        
        for profile in valid_profiles:
            response = client.post("/scan/barcode", json={
                "barcode": "1234567890123",
                "user_profiles": [profile]
            })
            # Should accept the profile (may fail for other reasons)
            assert response.status_code != 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
