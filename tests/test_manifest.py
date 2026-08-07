"""Tests keeping the packaging metadata aligned with the tested versions."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / "custom_components" / "tplink_deco" / "manifest.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
HACS_PATH = REPO_ROOT / "hacs.json"


def _dev_group_pin(package: str) -> str:
    pyproject = tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))
    for requirement in pyproject["dependency-groups"]["dev"]:
        name, separator, version = requirement.partition("==")
        if name == package and separator:
            return version
    message = f"{package} is not pinned in the dev dependency group"
    raise AssertionError(message)


def test_manifest_installs_the_sdk_version_the_tests_run_against() -> None:
    """The runtime requirement must match the pin the test suite validates."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = f"tplink-deco-api=={_dev_group_pin('tplink-deco-api')}"
    assert manifest["requirements"] == [expected]


def test_hacs_floor_is_the_home_assistant_version_the_tests_run_against() -> None:
    """The advertised minimum Home Assistant version must be a tested one."""
    hacs = json.loads(HACS_PATH.read_text(encoding="utf-8"))
    assert hacs["homeassistant"] == _dev_group_pin("homeassistant")
