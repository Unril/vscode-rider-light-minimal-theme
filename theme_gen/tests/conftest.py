"""Shared test fixtures."""

import pytest

from theme_gen.pipeline import ThemeDocument, build_theme_document


@pytest.fixture(scope="session")
def theme_output() -> ThemeDocument:
    """Session-scoped fixture: full light theme dict generated once per test run."""
    return build_theme_document(is_dark=False)


@pytest.fixture(scope="session")
def dark_theme_output() -> ThemeDocument:
    """Session-scoped fixture: full dark theme dict generated once per test run."""
    return build_theme_document(is_dark=True)
