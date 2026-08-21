"""HU-09, Historia 3: the origin allow-list is explicit, never a wildcard."""

import pytest

from core.settings.default import AppSettings


def test_origins_are_parsed_from_a_comma_separated_list() -> None:
    settings = AppSettings(CORS_ALLOWED_ORIGINS="https://a.dev, https://b.dev ")
    assert settings.cors_origins == ["https://a.dev", "https://b.dev"]


def test_a_wildcard_is_allowed_in_development() -> None:
    settings = AppSettings(ENVIRONMENT="development", CORS_ALLOWED_ORIGINS="*")
    assert settings.cors_origins == ["*"]


def test_a_wildcard_fails_loudly_in_production() -> None:
    """Better a crash at boot than a world-open API nobody noticed."""
    settings = AppSettings(ENVIRONMENT="production", CORS_ALLOWED_ORIGINS="*")
    with pytest.raises(ValueError, match="must not contain"):
        _ = settings.cors_origins


def test_production_accepts_an_explicit_list() -> None:
    settings = AppSettings(
        ENVIRONMENT="production",
        CORS_ALLOWED_ORIGINS="https://project-jackpot.up.railway.app",
    )
    assert settings.cors_origins == ["https://project-jackpot.up.railway.app"]
