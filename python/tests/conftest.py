# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from pathlib import Path

import pytest
from pytest import MonkeyPatch

from insta_science import CURRENT_PLATFORM, Platform


@pytest.fixture
def platform() -> Platform:
    return CURRENT_PLATFORM


@pytest.fixture
def pyproject_toml(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    project_dir.mkdir(parents=True)
    pyproject_toml = project_dir / "pyproject.toml"
    monkeypatch.setenv("INSTA_SCIENCE_CONFIG", str(pyproject_toml))
    return pyproject_toml


@pytest.fixture
def expected_v0_9_0_url(platform) -> str:
    expected_binary_name = platform.qualified_binary_name("science-fat")
    return f"https://github.com/a-scie/lift/releases/download/v0.9.0/{expected_binary_name}"


@pytest.fixture
def expected_v0_9_0_size(platform) -> int:
    if platform is Platform.Linux_aarch64:
        return 21092144
    if platform is Platform.Linux_armv7l:
        return 20570562
    if platform is Platform.Linux_x86_64:
        return 24784994

    if platform is Platform.Macos_aarch64:
        return 18619230
    if platform is Platform.Macos_aarch64:
        return 19098999

    if platform is Platform.Windows_aarch64:
        return 24447228
    if platform is Platform.Windows_x86_64:
        return 24615918

    pytest.skip(f"Unsupported platform for science v0.9.0: {platform}")


@pytest.fixture
def expected_v0_9_0_fingerprint(platform) -> str:
    if platform is Platform.Linux_aarch64:
        return "e9b1ad6731ed22d528465fd1464a6183b43e7a7aa54211309bbe9fc8894e85ac"
    if platform is Platform.Linux_armv7l:
        return "1935c90c527d13ec0c46db4718a0d5f9050d264d08ba222798b8f47836476b7d"
    if platform is Platform.Linux_x86_64:
        return "37ce3ed19f558e2c18d3339a4a5ee40de61a218b7a42408451695717519c4160"

    if platform is Platform.Macos_aarch64:
        return "e6fffeb0e8abd7e16af317aad97cb9852b18f0302f36a9022f3e76f3c2cca1ef"
    if platform is Platform.Macos_aarch64:
        return "640487cb1402d5edd6f86c9acaad6b18d1ddd553375db50d06480cccf4fccd7e"

    if platform is Platform.Windows_aarch64:
        return "e0f1b08c4701681b726315f8f1b86a4d7580240abfc1c0a7c6a2ba024da4d558"
    if platform is Platform.Windows_x86_64:
        return "722030eb6bb5f9510acd5b737eda2b735918ee28df4b93d297a9dfa54fc4d6fb"

    pytest.skip(f"Unsupported platform for science v0.9.0: {platform}")
