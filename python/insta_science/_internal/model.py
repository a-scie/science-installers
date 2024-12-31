# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import errno
import subprocess
import urllib.parse
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import PurePath
from subprocess import CalledProcessError
from typing import NewType

from packaging.version import Version

from .hashing import Digest

VersionError = NewType("VersionError", str)


@dataclass(frozen=True)
class ScienceExe:
    path: PurePath
    _version: Version | None = field(default=None, hash=False, compare=False)

    def version(self) -> Version | VersionError:
        if self._version is not None:
            return self._version

        try:
            version = Version(
                subprocess.run(
                    args=[self.path, "-V"], text=True, stdout=subprocess.PIPE
                ).stdout.strip()
            )
        except CalledProcessError as e:
            return VersionError(str(e))
        except OSError as e:
            if e.errno == errno.ENOEXEC:
                # A foreign platform science binary.
                return VersionError(str(e))
            raise
        else:
            object.__setattr__(self, "_version", version)
            return version


class Url(str):
    @cached_property
    def info(self):
        return urllib.parse.urlparse(self)


@dataclass(frozen=True)
class Science:
    @classmethod
    def spec(
        cls, version: str, digest: Digest | None = None, base_url: Url | None = None
    ) -> Science:
        science_version = Version(version)
        return (
            cls(version=science_version, digest=digest, base_url=base_url)
            if base_url
            else cls(version=science_version, digest=digest)
        )

    version: Version | None = None
    digest: Digest | None = None
    base_url: Url = Url("https://github.com/a-scie/lift/releases")

    def exe(self, path: PurePath) -> ScienceExe:
        return ScienceExe(path=path, _version=self.version)


@dataclass(frozen=True)
class Configuration:
    science: Science = Science()
    cache: PurePath | None = None
