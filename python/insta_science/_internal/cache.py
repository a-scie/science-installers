# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import atexit
import hashlib
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path, PurePath
from typing import Iterator, Union

import appdirs
from filelock import FileLock
from typing_extensions import TypeAlias

from .du import DiskUsage


@dataclass(frozen=True)
class Complete:
    path: Path


@dataclass(frozen=True)
class Missing:
    path: Path
    work: Path


CacheResult: TypeAlias = Union[Complete, Missing]


@dataclass(frozen=True)
class DownloadCache:
    _TTL_EXPIRY_FORMAT = "%m/%d/%y %H:%M:%S"
    _CACHED_EXT = ".cached"

    # Bump this when changing cache layout.
    _CACHE_VERSION = 1

    base_dir: Path

    @property
    def _base(self) -> Path:
        return self.base_dir / str(self._CACHE_VERSION)

    @contextmanager
    def get_or_create(
        self, url: str, *, namespace: str, ttl: timedelta | None = None
    ) -> Iterator[CacheResult]:
        """A context manager that yields a `cache result.

        If the cache result is `Missing`, the block yielded to should materialize the given url
        to the `Missing.work` path. Upon successful exit from this context manager, the given url's
        content will exist at the cache result path.
        """
        cached_file = (
            self._base / namespace / f"{hashlib.sha256(url.encode()).hexdigest()}{self._CACHED_EXT}"
        )

        ttl_file = cached_file.with_suffix(".ttl") if ttl else None
        if ttl_file and not ttl_file.exists():
            cached_file.unlink(missing_ok=True)
        elif ttl_file:
            try:
                datetime_object = datetime.strptime(
                    ttl_file.read_text().strip(), self._TTL_EXPIRY_FORMAT
                )
                if datetime.now() > datetime_object:
                    cached_file.unlink(missing_ok=True)
            except ValueError:
                cached_file.unlink(missing_ok=True)

        if cached_file.exists():
            yield Complete(path=cached_file)
            return

        cached_file.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(str(cached_file.with_name(f"{cached_file.name}.lck"))):
            if cached_file.exists():
                yield Complete(path=cached_file)
                return

            work = cached_file.with_name(f"{cached_file.name}.work")
            work.unlink(missing_ok=True)
            atexit.register(work.unlink, missing_ok=True)
            yield Missing(path=cached_file, work=work)
            if not work.exists():
                return
            work.rename(cached_file)
            if ttl_file and ttl:
                ttl_file.write_text((datetime.now() + ttl).strftime(self._TTL_EXPIRY_FORMAT))

    def iter_entries(self, *, namespace: str | None = None) -> Iterator[Path]:
        try:
            for path in (self._base / namespace if namespace else self._base).iterdir():
                if path.suffix == self._CACHED_EXT:
                    yield path
        except FileNotFoundError:
            pass

    def usage(self) -> DiskUsage:
        return DiskUsage.collect(str(self._base))


def download_cache(cache_dir: PurePath | None = None) -> DownloadCache:
    return DownloadCache(
        base_dir=Path(
            os.path.expanduser(
                os.environ.get(
                    "INSTA_SCIENCE_CACHE",
                    (
                        str(cache_dir)
                        if cache_dir
                        else appdirs.user_cache_dir(appname="insta-science", appauthor=False)
                    ),
                )
            )
        )
    )
