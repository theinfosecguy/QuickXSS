from __future__ import annotations

import pytest

from quickxss.scan.errors import ValidationError
from quickxss.scan.io import validate_domain, validate_output_name


def test_validate_domain_ok() -> None:
    assert validate_domain("example.com") == "example.com"


def test_validate_domain_rejects_path() -> None:
    with pytest.raises(ValidationError):
        validate_domain("example.com/evil")


def test_validate_output_name_ok() -> None:
    assert validate_output_name("results.txt") == "results.txt"


def test_validate_output_name_rejects_path() -> None:
    with pytest.raises(ValidationError):
        validate_output_name("../results.txt")
