# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import PurePath
from typing import Iterator

from packaging.version import Version

from .cache import DownloadCache
from .fetcher import fetch_and_verify
from .hashing import Digest, Fingerprint
from .model import Science, ScienceExe, Url
from .platform import CURRENT_PLATFORM, Platform

_DOWNLOAD_NAMESPACE = "url-exes"


@dataclass(frozen=True)
class _LoadResult:
    path: PurePath
    binary_name: str


def _load_project_release(
    cache: DownloadCache,
    base_url: Url,
    binary_name: str,
    version: Version | None = None,
    fingerprint: Digest | Fingerprint | None = None,
    platform: Platform = CURRENT_PLATFORM,
) -> _LoadResult:
    qualified_binary_name = platform.qualified_binary_name(binary_name)
    if version:
        version_path = f"download/v{version}"
        ttl = None
    else:
        version_path = "latest/download"
        ttl = timedelta(days=5)
    path = fetch_and_verify(
        url=Url(f"{base_url}/{version_path}/{qualified_binary_name}"),
        cache=cache,
        namespace=_DOWNLOAD_NAMESPACE,
        fingerprint=fingerprint,
        executable=True,
        ttl=ttl,
    )
    return _LoadResult(path=path, binary_name=qualified_binary_name)


def science(
    cache: DownloadCache, spec: Science = Science(), platform: Platform = CURRENT_PLATFORM
) -> ScienceExe:
    return spec.exe(
        _load_project_release(
            cache=cache,
            base_url=spec.base_url,
            binary_name="science-fat",
            version=spec.version,
            fingerprint=spec.digest,
            platform=platform,
        ).path
    )


def iter_science_exes(cache: DownloadCache) -> Iterator[ScienceExe]:
    for path in cache.iter_entries(namespace=_DOWNLOAD_NAMESPACE):
        yield ScienceExe(path)
