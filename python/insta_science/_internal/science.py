# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import shutil
import subprocess
from datetime import timedelta
from pathlib import Path, PurePath
from subprocess import CalledProcessError

import httpx
from packaging.version import Version

from . import a_scie, parser, project
from .cache import DOWNLOAD_CACHE, Missing
from .errors import InputError, ScienceNotFound
from .hashing import ExpectedDigest
from .model import Science
from .platform import CURRENT_PLATFORM


def _find_science_on_path(spec: Science) -> PurePath | None:
    url = "file://<just-a-cache-key>/science"
    ttl: timedelta | None = None
    if spec.version:
        url = f"{url}/v{spec.version}"
        if spec.digest:
            url = f"{url}#{spec.digest.fingerprint}:{spec.digest.size}"
    else:
        ttl = timedelta(days=5)

    with DOWNLOAD_CACHE.get_or_create(url=url, ttl=ttl) as cache_result:
        if isinstance(cache_result, Missing):
            for binary_name in (
                CURRENT_PLATFORM.binary_name("science"),
                CURRENT_PLATFORM.binary_name("science-fat"),
                CURRENT_PLATFORM.qualified_binary_name("science"),
                CURRENT_PLATFORM.qualified_binary_name("science-fat"),
            ):
                science_exe = shutil.which(binary_name)
                if not science_exe:
                    continue
                if spec.version:
                    if spec.version != Version(
                        subprocess.run(
                            args=[science_exe, "-V"], text=True, stdout=subprocess.PIPE
                        ).stdout.strip()
                    ):
                        continue
                    if spec.digest and spec.digest.fingerprint:
                        expected_digest = ExpectedDigest(
                            fingerprint=spec.digest.fingerprint, size=spec.digest.size
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
    if spec is None:
        pyproject_toml = project.find_pyproject_toml()
        spec = parser.configured_science(pyproject_toml) if pyproject_toml else Science()

    try:
        return _find_science_on_path(spec) or a_scie.science(spec)
    except (
        OSError,
        CalledProcessError,
        httpx.HTTPError,
        httpx.InvalidURL,
        httpx.CookieConflict,
        httpx.StreamError,
    ) as e:
        raise ScienceNotFound(str(e))
