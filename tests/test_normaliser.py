"""Tests for ingredient normalization module."""

import pytest
from src.preprocessing.ingredient_normaliser import (
    IngredientNormaliser,
    normalise_ingredient_list,
    normalise_ingredient_name,
)


class TestIngredientNormaliser:
    """Test cases for IngredientNormaliser class."""

    @pytest.fixture
    def normaliser(self):
        """Create normaliser instance for tests."""
        return IngredientNormaliser()

    def test_aqua_normalizes_to_water(self, normaliser):
        """Test that 'Aqua' normalizes to 'water'."""
        assert normaliser.normalise_ingredient_name("Aqua") == "water"
        assert normaliser.normalise_ingredient_name("AQUA") == "water"
        assert normaliser.normalise_ingredient_name("aqua") == "water"

    def test_color_code_normalization(self, normaliser):
        """Test that CI color codes normalize correctly."""
        assert normaliser.normalise_ingredient_name("CI 77891") == "titanium dioxide"
        assert normaliser.normalise_ingredient_name("ci 77891") == "titanium dioxide"

    def test_fragrance_mapping(self, normaliser):
        """Test fragrance alias mapping."""
        assert normaliser.normalise_ingredient_name("parfum") == "fragrance"
        assert normaliser.normalise_ingredient_name("fragrance") == "fragrance"

    def test_preservative_variants(self, normaliser):
        """Test that paraben variants normalize correctly."""
        assert normaliser.normalise_ingredient_name("methylparaben") == "methylparaben"
        assert normaliser.normalise_ingredient_name("ethylparaben") == "ethylparaben"

    def test_comma_separated_splitting(self, normaliser):
        """Test comma-separated ingredient list parsing."""
        raw_text = "Water, Glycerin, Fragrance"
        result = normaliser.normalise_ingredient_list(raw_text)
        assert "water" in result
        assert "glycerin" in result
        assert "fragrance" in result

    def test_nested_parentheses_handling(self, normaliser):
        """Test that nested parentheses are handled correctly."""
        raw_text = "Aqua (Water), Glycerin (20%), CI 77891 (Titanium Dioxide)"
        result = normaliser.normalise_ingredient_list(raw_text)
        assert "water" in result
        assert "glycerin" in result
        assert "titanium dioxide" in result

    def test_percentage_removal(self, normaliser):
        """Test that percentages are removed from ingredient names."""
        raw_text = "Water 80%, Glycerin 5%, Fragrance 0.5%"
        result = normaliser.normalise_ingredient_list(raw_text)
        # Should contain normalized names without percentages
        assert len(result) > 0
        assert all("%" not in ing for ing in result)

    def test_mixed_language_handling(self, normaliser):
        """Test mixed language ingredient labels."""
        # This should not raise an error and should extract at least some ingredients
        raw_text = "पानी (Aqua), Glycerin, ग्लिसरीन"
        result = normaliser.normalise_ingredient_list(raw_text)
        # Should handle gracefully without crashing
        assert isinstance(result, list)

    def test_empty_string_handling(self, normaliser):
        """Test that empty strings are handled correctly."""
        assert normaliser.normalise_ingredient_list("") == []
        assert normaliser.normalise_ingredient_list("   ") == []

    def test_duplicate_removal(self, normaliser):
        """Test that duplicate ingredients are removed."""
        raw_text = "Water, Water, Glycerin, Water"
        result = normaliser.normalise_ingredient_list(raw_text)
        # 'water' should appear only once
        water_count = sum(1 for ing in result if ing == "water")
        assert water_count == 1

    def test_unknown_ingredient_passthrough(self, normaliser):
        """Test that unknown ingredients are returned as-is."""
        unknown = "some_rare_ingredient_xyz"
        result = normaliser.normalise_ingredient_name(unknown)
        # Should return the ingredient (normalized case) if not in mapping
        assert isinstance(result, str)


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_normalise_ingredient_name_function(self):
        """Test module-level normalise_ingredient_name function."""
        assert normalise_ingredient_name("Aqua") == "water"
        assert normalise_ingredient_name("CI 77891") == "titanium dioxide"

    def test_normalise_ingredient_list_function(self):
        """Test module-level normalise_ingredient_list function."""
        raw_text = "Water, Glycerin, Fragrance"
        result = normalise_ingredient_list(raw_text)
        assert "water" in result
        assert "glycerin" in result

    def test_split_ingredients_with_complex_parentheses(self):
        """Test ingredient splitting with complex parenthetical structures."""
        normaliser = IngredientNormaliser()
        text = "Aqua, Sodium Hydroxide, Water (Aqua), Glycerin (20%, Vegetables)"
        # Should not raise exception
        result = normaliser._split_ingredients(text)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
