# tests/test_utils.py

import pytest
from utils import validate_city_input, celsius_to_fahrenheit


def test_validate_city_input_strips_whitespace():
    assert validate_city_input("  Paris  ") == "Paris"


def test_validate_city_input_rejects_empty():
    with pytest.raises(ValueError):
        validate_city_input("   ")


def test_celsius_to_fahrenheit():
    assert celsius_to_fahrenheit(0) == 32
