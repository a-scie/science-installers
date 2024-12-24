# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import subprocess
from pathlib import Path
from textwrap import dedent

import pytest
from packaging.version import Version
from pytest import MonkeyPatch


def get_science_exe_version_via_insta_science() -> Version:
    return Version(
        subprocess.run(
            args=["insta-science", "-V"], text=True, stdout=subprocess.PIPE, check=True
        ).stdout.strip()
    )


def assert_science_exe_version_via_insta_science(expected_version: str) -> None:
    assert Version(expected_version) == get_science_exe_version_via_insta_science()


def test_self() -> None:
    assert get_science_exe_version_via_insta_science() >= Version("0.10.0"), (
        "By default insta-science should fetch the latest science version, which was 0.10.0 at "
        "the time this test was 1st introduced."
    )


@pytest.fixture(autouse=True)
def cache_dir(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("INSTA_SCIENCE_CACHE", str(cache_dir))
    return cache_dir


def test_version(pyproject_toml: Path) -> None:
    pyproject_toml.write_text(
        dedent(
            """\
            [tool.insta-science.science]
            version = "0.9.0"
            """
        )
    )
    assert_science_exe_version_via_insta_science("0.9.0")


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
    assert_science_exe_version_via_insta_science("0.9.0")


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
