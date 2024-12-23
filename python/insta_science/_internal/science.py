# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import timedelta
from pathlib import Path, PurePath
from subprocess import CalledProcessError

import colors
import httpx
from packaging.version import Version

from . import a_scie, parser, project
from .cache import Missing, download_cache
from .errors import InputError, ScienceNotFound
from .hashing import ExpectedDigest
from .model import Science
from .platform import Platform


def _find_science_on_path(science: Science) -> PurePath | None:
    url = "file://<just-a-cache-key>/science"
    ttl: timedelta | None = None
    if science.version:
        url = f"{url}/v{science.version}"
        if science.digest:
            url = f"{url}#{science.digest.fingerprint}:{science.digest.size}"
    else:
        ttl = timedelta(days=5)

    with download_cache().get_or_create(url=url, ttl=ttl) as cache_result:
        if isinstance(cache_result, Missing):
            current_platform = Platform.current()
            for binary_name in (
                current_platform.binary_name("science"),
                current_platform.binary_name("science-fat"),
                current_platform.qualified_binary_name("science"),
                current_platform.qualified_binary_name("science-fat"),
            ):
                science_exe = shutil.which(binary_name)
                if not science_exe:
                    continue
                if science.version:
                    if science.version != Version(
                        subprocess.run(
                            args=[science_exe, "-V"], text=True, stdout=subprocess.PIPE
                        ).stdout.strip()
                    ):
                        continue
                    if science.digest and science.digest.fingerprint:
                        expected_digest = ExpectedDigest(
                            fingerprint=science.digest.fingerprint, size=science.digest.size
                        )
                        try:
                            expected_digest.check_path(Path(science_exe))
                        except InputError:
                            continue
                shutil.copy(science_exe, cache_result.work)
                return cache_result.path
            return None
    return cache_result.path


def ensure_installed(spec: Science | None = None) -> PurePath:
    """Ensures an appropriate science binary is installed and returns its path.

    Args:
        spec: An optional specification of which science binary is required.

    Returns:
        The path of a science binary meeting the supplied ``spec``, if any.

    Raises:
        InputError: No ``spec`` was supplied ; so the information about which ``science`` binary to
            install was parsed from ``pyproject.toml`` and found to have errors.
        ScienceNotFound: The science binary could not be found locally or downloaded.
    """
    if spec is not None:
        science = spec
    else:
        try:
            pyproject_toml = project.find_pyproject_toml()
            science = parser.configured_science(pyproject_toml) if pyproject_toml else Science()
        except InputError as e:
            sys.exit(f"{colors.red('Configuration error')}: {colors.yellow(str(e))}")

    try:
        return _find_science_on_path(science) or a_scie.science(science)
    except (
        OSError,
        CalledProcessError,
        httpx.HTTPError,
        httpx.InvalidURL,
        httpx.CookieConflict,
        httpx.StreamError,
    ) as e:
        raise ScienceNotFound(str(e))
