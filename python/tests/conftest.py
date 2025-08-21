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
def expected_v0_13_0_url(platform: Platform, libc: LibC | None) -> str:
    expected_binary_name = platform.qualified_binary_name("science-fat", libc=libc)
    return f"https://github.com/a-scie/lift/releases/download/v0.13.0/{expected_binary_name}"


@pytest.fixture
def expected_v0_13_0_size(platform: Platform, libc: LibC | None) -> int:
    if platform is Platform.Linux_aarch64:
        return 30138165
    if platform is Platform.Linux_armv7l:
        return 26968578
    if platform is Platform.Linux_powerpc64le:
        return 29278663
    if platform is Platform.Linux_riscv64:
        return 27160998
    if platform is Platform.Linux_s390x:
        return 30123692
    if platform is Platform.Linux_x86_64:
        if libc is LibC.MUSL:
            return 29704768
        else:
            return 36308054

    if platform is Platform.Macos_aarch64:
        return 19180565
    if platform is Platform.Macos_x86_64:
        return 19678576

    if platform is Platform.Windows_aarch64:
        return 24698389
    if platform is Platform.Windows_x86_64:
        return 25075180

    pytest.skip(f"Unsupported platform for science v0.13.0: {platform}")


@pytest.fixture
def expected_v0_13_0_fingerprint(platform: Platform, libc: LibC | None) -> str:
    if platform is Platform.Linux_aarch64:
        return "15103566e979b4eb82fa6b918f3e54772a287a42948a33dc83d0d152ffa207cb"
    if platform is Platform.Linux_armv7l:
        return "0da05c60a243bb93c7c71829cd4720327e9ec72d594ecf264ea5d722f4d595a6"
    if platform is Platform.Linux_powerpc64le:
        return "5d0048534ea991deaa5a2dc2ecad9855a6c29c08ad829723de8f708f24eb1574"
    if platform is Platform.Linux_riscv64:
        return "731164031ade194acc7be2367178d3d43cc89ebfa8b220f7585e5874d2e99ce7"
    if platform is Platform.Linux_s390x:
        return "3b529c038615e974a8af1a9db52cf736fef2f99167eb6e1bdde74f61f9c039d7"
    if platform is Platform.Linux_x86_64:
        if libc is LibC.MUSL:
            return "398e2416ccecdabf15525078edf4271d23e42399fcc375d4f5d1228c68eff836"
        else:
            return "2146c55b4fcd3c7b524b29e3014cca851372219340968967a6086d399db2c48e"

    if platform is Platform.Macos_aarch64:
        return "2a2739d688d687c8ec576162500f7cb5f00d798c11b46009bd94a60d8a0d0fff"
    if platform is Platform.Macos_x86_64:
        return "576a67b467663ee9c2cfcead73b1b575c85addd9d9ffd3b7891ef3552d79a0ee"

    if platform is Platform.Windows_aarch64:
        return "7905b56ed6f918f3b7eb795cf9f54ee5dba5b2e0817c63c683e70cb9ba21b420"
    if platform is Platform.Windows_x86_64:
        return "8f466eeba296618b408a43273309f6d16193541bbe1bcbd9de29474ed3b9d7c8"

    pytest.skip(f"Unsupported platform for science v0.13.0: {platform}")
