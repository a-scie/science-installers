# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from pathlib import Path

import pytest
from pytest import MonkeyPatch

from insta_science import CURRENT_PLATFORM, Platform
from insta_science._internal import CURRENT_LIBC, LibC


@pytest.fixture
def platform() -> Platform:
    return CURRENT_PLATFORM


@pytest.fixture
def libc() -> LibC | None:
    return CURRENT_LIBC


@pytest.fixture
def pyproject_toml(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    project_dir.mkdir(parents=True)
    pyproject_toml = project_dir / "pyproject.toml"
    monkeypatch.setenv("INSTA_SCIENCE_CONFIG", str(pyproject_toml))
    return pyproject_toml


@pytest.fixture
def expected_v0_12_0_url(platform: Platform, libc: LibC | None) -> str:
    expected_binary_name = platform.qualified_binary_name("science-fat", libc=libc)
    return f"https://github.com/a-scie/lift/releases/download/v0.12.0/{expected_binary_name}"


@pytest.fixture
def expected_v0_12_0_size(platform: Platform, libc: LibC | None) -> int:
    if platform is Platform.Linux_aarch64:
        return 21174202
    if platform is Platform.Linux_armv7l:
        return 20649465
    if platform is Platform.Linux_powerpc64le:
        return 22214859
    if platform is Platform.Linux_s390x:
        return 22882497
    if platform is Platform.Linux_x86_64:
        if libc is LibC.MUSL:
            return 22022099
        else:
            return 24833023

    if platform is Platform.Macos_aarch64:
        return 18782784
    if platform is Platform.Macos_x86_64:
        return 19135116

    if platform is Platform.Windows_aarch64:
        return 24592697
    if platform is Platform.Windows_x86_64:
        return 24749565

    pytest.skip(f"Unsupported platform for science v0.9.0: {platform}")


@pytest.fixture
def expected_v0_12_0_fingerprint(platform: Platform, libc: LibC | None) -> str:
    if platform is Platform.Linux_aarch64:
        return "ceabee3840813e316e31cc1f2b958ecb02e4d8ee77bea6e35bd7b5eec947e046"
    if platform is Platform.Linux_armv7l:
        return "9a923936a976f2d49c683849219f8eb23618d52e26cbb3c5b30fd12f3974110b"
    if platform is Platform.Linux_powerpc64le:
        return "7b78225517dca85ec59120d02482d910413247641dad5c3f7fa7c2965ad9c8a6"
    if platform is Platform.Linux_s390x:
        return "7ac30ebb03bed4314d15168c43cb35c2c488712ebaf7ea333cba88091b89f610"
    if platform is Platform.Linux_x86_64:
        if libc is LibC.MUSL:
            return "c34c74cdd8c547e242ee5a6aa4d0f5606ff019a86388a75a4e544c5e648c313f"
        else:
            return "aba969b7dd006d330f49b6a0c0844f0850df8c932ec57db6cb442efbcbaf94b5"

    if platform is Platform.Macos_aarch64:
        return "4656b73a981196e61bb1b4a874d09ffbc44ff402a88195d557963e97e0d76efc"
    if platform is Platform.Macos_x86_64:
        return "910f571ba77c21d791b60c4cd44a0571a58b090f625ba64c24dfffce693bd530"

    if platform is Platform.Windows_aarch64:
        return "472226f99e57d3a10c43a86f10f7a7e6c50d3434e16414081e6039dd90fce660"
    if platform is Platform.Windows_x86_64:
        return "4d432ed91f215e5ca5d8d09ee42c8d0158a265ed66784877310f491d98d7298e"

    pytest.skip(f"Unsupported platform for science v0.9.0: {platform}")
