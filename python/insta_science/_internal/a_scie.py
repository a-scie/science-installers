# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import PurePath

from packaging.version import Version

from .fetcher import fetch_and_verify
from .hashing import Digest, Fingerprint
from .model import Science, Url
from .platform import CURRENT_PLATFORM, Platform


@dataclass(frozen=True)
class _LoadResult:
    path: PurePath
    binary_name: str


def _load_project_release(
    project_name: str,
    binary_name: str,
    version: Version | None = None,
    fingerprint: Digest | Fingerprint | None = None,
    platform: Platform = CURRENT_PLATFORM,
) -> _LoadResult:
    qualified_binary_name = platform.qualified_binary_name(binary_name)
    base_url = f"https://github.com/a-scie/{project_name}/releases"
    if version:
        version_path = f"download/v{version}"
        ttl = None
    else:
        version_path = "latest/download"
        ttl = timedelta(days=5)
    path = fetch_and_verify(
        url=Url(f"{base_url}/{version_path}/{qualified_binary_name}"),
        fingerprint=fingerprint,
        executable=True,
        ttl=ttl,
    )
    return _LoadResult(path=path, binary_name=qualified_binary_name)


def science(spec: Science | None = None, platform: Platform = CURRENT_PLATFORM) -> PurePath:
    version = spec.version if spec else None
    fingerprint = spec.digest if spec and spec.digest else None
    return _load_project_release(
        project_name="lift",
        binary_name="science-fat",
        version=version,
        fingerprint=fingerprint,
        platform=platform,
    ).path
