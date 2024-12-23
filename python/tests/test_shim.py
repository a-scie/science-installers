# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import subprocess
from pathlib import Path
from textwrap import dedent

import _pytest
import pytest
from packaging.version import Version

from insta_science import Platform


def test_self() -> None:
    subprocess.run(args=["insta-science", "-V"], check=True)


@pytest.fixture(autouse=True)
def cache_dir(monkeypatch: _pytest.monkeypatch, tmp_path: Path) -> Path:
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("INSTA_SCIENCE_CACHE", str(cache_dir))
    return cache_dir


@pytest.fixture
def pyproject_toml(monkeypatch: _pytest.monkeypatch, tmp_path: Path) -> Path:
    project_dir = tmp_path / "project"
    project_dir.mkdir(parents=True)
    pyproject_toml = project_dir / "pyproject.toml"
    monkeypatch.setenv("INSTA_SCIENCE_CONFIG", str(pyproject_toml))
    return pyproject_toml


def test_version(pyproject_toml: Path) -> None:
    pyproject_toml.write_text(
        dedent(
            """\
            [tool.insta-science.science]
            version = "0.9.0"
            """
        )
    )
    assert Version("0.9.0") == Version(
        subprocess.run(
            args=["insta-science", "-V"], text=True, stdout=subprocess.PIPE, check=True
        ).stdout.strip()
    )


@pytest.fixture
def platform() -> Platform:
    return Platform.current()


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


def test_digest(
    pyproject_toml: Path, expected_v0_9_0_size: int, expected_v0_9_0_fingerprint: str
) -> None:
    pyproject_toml.write_text(
        dedent(
            f"""\
            [tool.insta-science.science]
            version = "0.9.0"
            [tool.insta-science.science.digest]
            size = {expected_v0_9_0_size}
            fingerprint = "{expected_v0_9_0_fingerprint}"
            """
        )
    )
    assert Version("0.9.0") == Version(
        subprocess.run(
            args=["insta-science", "-V"], text=True, stdout=subprocess.PIPE, check=True
        ).stdout.strip()
    )


def test_size_mismatch(
    pyproject_toml: Path,
    expected_v0_9_0_url: str,
    expected_v0_9_0_size: int,
    expected_v0_9_0_fingerprint: str,
) -> None:
    pyproject_toml.write_text(
        dedent(
            f"""\
            [tool.insta-science.science]
            version = "0.9.0"
            [tool.insta-science.science.digest]
            size = 1
            fingerprint = "{expected_v0_9_0_fingerprint}"
            """
        )
    )

    process = subprocess.run(args=["insta-science", "-V"], text=True, stderr=subprocess.PIPE)
    assert process.returncode != 0
    assert (
        f"The content at {expected_v0_9_0_url} is expected to be 1 bytes, but advertises a Content-Length of {expected_v0_9_0_size} bytes."
    ) in process.stderr


def test_fingerprint_mismatch(
    pyproject_toml: Path,
    expected_v0_9_0_url: str,
    expected_v0_9_0_size: int,
    expected_v0_9_0_fingerprint: str,
) -> None:
    pyproject_toml.write_text(
        dedent(
            f"""\
            [tool.insta-science.science]
            version = "0.9.0"
            [tool.insta-science.science.digest]
            size={expected_v0_9_0_size}
            fingerprint="XXX"
            """
        )
    )

    process = subprocess.run(args=["insta-science", "-V"], text=True, stderr=subprocess.PIPE)
    assert process.returncode != 0
    assert (
        f"The download from {expected_v0_9_0_url} has unexpected contents.\n"
        f"Expected sha256 digest:\n"
        f"  XXX\n"
        f"Actual sha256 digest:\n"
        f"  {expected_v0_9_0_fingerprint}"
    ) in process.stderr
