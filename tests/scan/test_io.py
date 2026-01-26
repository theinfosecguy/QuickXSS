"""Unit tests for quickxss.scan.io module."""

from __future__ import annotations

from pathlib import Path

import pytest

from quickxss.scan.errors import OperationError, ValidationError
from quickxss.scan.io import (
    dedupe_preserve_order,
    ensure_scan_paths,
    validate_domain,
    validate_output_name,
    write_lines,
)


def test_validate_domain_ok() -> None:
    """Valid domain should pass."""
    assert validate_domain("example.com") == "example.com"


def test_validate_domain_strips_whitespace() -> None:
    """Domain with whitespace should be stripped."""
    assert validate_domain("  example.com  ") == "example.com"


def test_validate_domain_rejects_forward_slash() -> None:
    """Domain with forward slash should be rejected."""
    with pytest.raises(ValidationError) as exc_info:
        validate_domain("example.com/evil")
    assert "path separators" in str(exc_info.value).lower()


def test_validate_domain_rejects_backslash() -> None:
    """Domain with backslash should be rejected."""
    with pytest.raises(ValidationError):
        validate_domain("example.com\\evil")


def test_validate_domain_rejects_double_dots() -> None:
    """Domain with double dots for traversal should be rejected."""
    with pytest.raises(ValidationError):
        validate_domain("..example.com")


def test_validate_domain_rejects_empty() -> None:
    """Empty domain should be rejected."""
    with pytest.raises(ValidationError) as exc_info:
        validate_domain("")
    assert "required" in str(exc_info.value).lower()


def test_validate_domain_rejects_whitespace_only() -> None:
    """Whitespace-only domain should be rejected."""
    with pytest.raises(ValidationError):
        validate_domain("   ")


def test_validate_output_name_ok() -> None:
    """Valid output name should pass."""
    assert validate_output_name("results.txt") == "results.txt"


def test_validate_output_name_strips_whitespace() -> None:
    """Output name with whitespace should be stripped."""
    assert validate_output_name("  results.txt  ") == "results.txt"


def test_validate_output_name_rejects_path() -> None:
    """Output name with path traversal should be rejected."""
    with pytest.raises(ValidationError):
        validate_output_name("../results.txt")


def test_validate_output_name_rejects_forward_slash() -> None:
    """Output name with forward slash should be rejected."""
    with pytest.raises(ValidationError):
        validate_output_name("dir/results.txt")


def test_validate_output_name_rejects_backslash() -> None:
    """Output name with backslash should be rejected."""
    with pytest.raises(ValidationError):
        validate_output_name("dir\\results.txt")


def test_validate_output_name_rejects_empty() -> None:
    """Empty output name should be rejected."""
    with pytest.raises(ValidationError) as exc_info:
        validate_output_name("")
    assert "required" in str(exc_info.value).lower()


def test_ensure_scan_paths_creates_directory(tmp_path: Path) -> None:
    """Should create base directory if it doesn't exist."""
    paths = ensure_scan_paths(tmp_path, "example.com", "results.txt", False)
    assert paths.base_dir.exists()
    assert paths.base_dir == tmp_path / "example.com"


def test_ensure_scan_paths_returns_correct_paths(tmp_path: Path) -> None:
    """Should return correct path objects."""
    paths = ensure_scan_paths(tmp_path, "test.com", "output.txt", False)
    assert paths.urls_file == tmp_path / "test.com" / "test.com.txt"
    assert paths.temp_xss_file == tmp_path / "test.com" / "test.com_temp_xss.txt"
    assert paths.xss_file == tmp_path / "test.com" / "test.com_xss.txt"
    assert paths.results_file == tmp_path / "test.com" / "output.txt"


def test_ensure_scan_paths_raises_if_exists_without_overwrite(tmp_path: Path) -> None:
    """Should raise ValidationError if directory exists and overwrite=False."""
    base = tmp_path / "existing.com"
    base.mkdir()
    with pytest.raises(ValidationError) as exc_info:
        ensure_scan_paths(tmp_path, "existing.com", "results.txt", False)
    assert "already exists" in str(exc_info.value).lower()


def test_ensure_scan_paths_allows_overwrite(tmp_path: Path) -> None:
    """Should allow existing directory when overwrite=True."""
    base = tmp_path / "existing.com"
    base.mkdir()
    (base / "old_file.txt").write_text("old content")

    paths = ensure_scan_paths(tmp_path, "existing.com", "results.txt", True)
    assert paths.base_dir.exists()
    assert (base / "old_file.txt").exists()


def test_ensure_scan_paths_nested_directory(tmp_path: Path) -> None:
    """Should create nested directories."""
    results_dir = tmp_path / "nested" / "results"
    paths = ensure_scan_paths(results_dir, "example.com", "results.txt", False)
    assert paths.base_dir.exists()


def test_write_lines_writes_content(tmp_path: Path) -> None:
    """Should write lines to file."""
    path = tmp_path / "test.txt"
    write_lines(path, ["line1", "line2", "line3"])
    content = path.read_text()
    assert content == "line1\nline2\nline3\n"


def test_write_lines_empty_creates_empty_file(tmp_path: Path) -> None:
    """Should create empty file for empty input."""
    path = tmp_path / "empty.txt"
    write_lines(path, [])
    assert path.exists()
    assert path.read_text() == ""


def test_write_lines_single_line(tmp_path: Path) -> None:
    """Should handle single line."""
    path = tmp_path / "single.txt"
    write_lines(path, ["only one"])
    assert path.read_text() == "only one\n"


def test_write_lines_raises_on_write_error(tmp_path: Path) -> None:
    """Should raise OperationError on write failure."""
    dir_path = tmp_path / "directory"
    dir_path.mkdir()
    with pytest.raises(OperationError):
        write_lines(dir_path, ["content"])


def test_dedupe_removes_duplicates() -> None:
    """Should remove duplicate lines."""
    result = dedupe_preserve_order(["a", "b", "a", "c", "b"])
    assert result == ["a", "b", "c"]


def test_dedupe_preserves_order() -> None:
    """Should preserve first occurrence order."""
    result = dedupe_preserve_order(["z", "y", "x", "y", "z"])
    assert result == ["z", "y", "x"]


def test_dedupe_empty_input() -> None:
    """Should handle empty input."""
    result = dedupe_preserve_order([])
    assert result == []


def test_dedupe_no_duplicates() -> None:
    """Should work with no duplicates."""
    result = dedupe_preserve_order(["a", "b", "c"])
    assert result == ["a", "b", "c"]


def test_dedupe_all_same() -> None:
    """Should handle all identical values."""
    result = dedupe_preserve_order(["x", "x", "x", "x"])
    assert result == ["x"]


def test_dedupe_generator_input() -> None:
    """Should work with generator input."""

    def gen():
        yield "a"
        yield "b"
        yield "a"

    result = dedupe_preserve_order(gen())
    assert result == ["a", "b"]
