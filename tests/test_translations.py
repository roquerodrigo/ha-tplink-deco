"""Tests keeping the translation locales and the entity keys in sync."""

from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path

import pytest

TRANSLATIONS_DIR = (
    Path(__file__).parent.parent / "custom_components" / "tplink_deco" / "translations"
)
TRANSLATED_PLATFORMS = ("binary_sensor", "sensor")


def _flatten_keys(data: object, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(data, dict):
        for key, value in data.items():
            full = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys |= _flatten_keys(value, full)
            else:
                keys.add(full)
    return keys


def _translation_files() -> list[Path]:
    return sorted(TRANSLATIONS_DIR.glob("*.json"))


def _authored_entity_keys(platform: str) -> set[str]:
    entity_section = json.loads(
        (TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"),
    )["entity"]
    return set(entity_section.get(platform, {}))


def _declared_entity_keys(platform: str) -> set[str]:
    package = importlib.import_module(f"custom_components.tplink_deco.{platform}")
    keys: set[str] = set()
    for module_info in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_info.name}")
        for candidate in vars(module).values():
            if getattr(candidate, "__module__", None) != module.__name__:
                continue
            description = getattr(candidate, "entity_description", None)
            translation_key = getattr(description, "translation_key", None)
            if translation_key is not None:
                keys.add(translation_key)
    return keys


def test_en_locale_exists() -> None:
    assert (TRANSLATIONS_DIR / "en.json").exists()


@pytest.mark.parametrize("locale", [f.stem for f in _translation_files()])
def test_translation_locale_matches_en_keys(locale: str) -> None:
    key_sets = {
        f.stem: _flatten_keys(json.loads(f.read_text(encoding="utf-8")))
        for f in _translation_files()
    }
    reference = key_sets["en"]
    other = key_sets[locale]
    missing = reference - other
    extra = other - reference
    assert not missing, f"{locale}.json is missing keys: {sorted(missing)}"
    assert not extra, f"{locale}.json has unexpected keys: {sorted(extra)}"


@pytest.mark.parametrize("platform", TRANSLATED_PLATFORMS)
def test_entity_translation_keys_match_authored_names(platform: str) -> None:
    """Every key an entity declares is authored, and nothing authored is dead."""
    authored = _authored_entity_keys(platform)
    declared = _declared_entity_keys(platform)
    unauthored = declared - authored
    dead = authored - declared
    assert not unauthored, f"{platform} keys missing from en.json: {sorted(unauthored)}"
    assert not dead, f"en.json has unused {platform} keys: {sorted(dead)}"
