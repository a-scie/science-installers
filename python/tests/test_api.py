# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from pathlib import Path
from textwrap import dedent

import pytest
from packaging.version import Version

from insta_science._internal import LibC, CURRENT_LIBC
from testing import is_exe

from insta_science import Digest, Science, ScienceExe, ensure_installed, CURRENT_PLATFORM, Platform


def assert_science_exe_version(science_exe: ScienceExe, expected_version: str) -> None:
    assert Version(expected_version) == science_exe.version()


def test_simple():
    science_exe = ensure_installed()
    assert is_exe(science_exe.path)
    assert science_exe.version() >= Version("0.10.0"), (
        "By default ensure_installed should fetch the latest science version, which was 0.10.0 at "
        "the time this test was 1st introduced."
    )


# TODO(John Sirois): Bump this test to use 0.12.0 when a newer science version is released and drop
#  the skip: https://github.com/a-scie/science-installers/issues/32
@pytest.mark.skipif(
    (CURRENT_PLATFORM, CURRENT_LIBC) == (Platform.Linux_x86_64, LibC.MUSL),
    reason="Only the latest release (0.12.0) supports 64 bit musl Linux."
)
def test_pyproject_toml_default(pyproject_toml: Path):
    pyproject_toml.write_text(
        dedent(
            """\
            [tool.insta-science.science]
            version = "0.11.3"
            """
        )
    )
    science_exe = ensure_installed()
    assert is_exe(science_exe.path)
    assert_science_exe_version(science_exe, "0.11.3")


def test_version_spec():
    science_exe = ensure_installed(spec=Science.spec(version="0.12.0"))
    assert is_exe(science_exe.path)
    assert_science_exe_version(science_exe, "0.12.0")


def test_digest_spec(expected_v0_12_0_size: int, expected_v0_12_0_fingerprint: str):
    science_exe = ensure_installed(
        spec=Science.spec(
            version="0.12.0",
            digest=Digest.spec(
                size=expected_v0_12_0_size, fingerprint=expected_v0_12_0_fingerprint
            ),
        )
    )
    assert is_exe(science_exe.path)
    assert_science_exe_version(science_exe, "0.12.0")
