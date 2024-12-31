# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import shutil
from datetime import timedelta
from pathlib import Path, PurePath
from subprocess import CalledProcessError
from typing import Iterator

import httpx

from . import a_scie, parser, project
from .cache import DownloadCache, Missing, download_cache
from .errors import InputError, ScienceNotFound
from .hashing import ExpectedDigest
from .model import Configuration, Science, ScienceExe
from .platform import CURRENT_PLATFORM

_PATH_EXES_NAMESPACE = "path-exes"


def _find_science_on_path(cache: DownloadCache, spec: Science) -> ScienceExe | None:
    url = "file://<just-a-cache-key>/science"
    ttl: timedelta | None = None
    if spec.version:
        url = f"{url}/v{spec.version}"
        if spec.digest:
            url = f"{url}#{spec.digest.fingerprint}:{spec.digest.size}"
    else:
        ttl = timedelta(days=5)

    with cache.get_or_create(url=url, namespace=_PATH_EXES_NAMESPACE, ttl=ttl) as cache_result:
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
                    if spec.version != ScienceExe(PurePath(science_exe)).version():
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
                return spec.exe(cache_result.path)
            return None
    return spec.exe(cache_result.path)


def ensure_installed(spec: Science | None = None, cache_dir: PurePath | None = None) -> ScienceExe:
    """Ensures an appropriate science binary is installed and returns its path.

    Args:
        spec: An optional specification of which science binary is required.
        cache_dir: An optional custom cache dir to use for caching the science binary.

    Returns:
        The path of a science binary meeting the supplied ``spec``, if any.

    Raises:
        InputError: No ``spec`` was supplied ; so the information about which ``science`` binary to
            install was parsed from ``pyproject.toml`` and found to have errors.
        ScienceNotFound: The science binary could not be found locally or downloaded.
    """
    if spec is None or cache_dir is None:
        pyproject_toml = project.find_pyproject_toml()
        configuration = (
            parser.parse_configuration(pyproject_toml) if pyproject_toml else Configuration()
        )
        cache_dir = cache_dir or configuration.cache
        spec = spec or configuration.science

    cache = download_cache(cache_dir=cache_dir)

    try:
        return _find_science_on_path(cache, spec) or a_scie.science(cache, spec)
    except (
        OSError,
        CalledProcessError,
        httpx.HTTPError,
        httpx.InvalidURL,
        httpx.CookieConflict,
        httpx.StreamError,
    ) as e:
        raise ScienceNotFound(str(e))


def iter_science_exes(cache: DownloadCache) -> Iterator[ScienceExe]:
    yield from a_scie.iter_science_exes(cache)
    for path in cache.iter_entries(namespace=_PATH_EXES_NAMESPACE):
        yield ScienceExe(path)
