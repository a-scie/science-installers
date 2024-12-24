# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from functools import cached_property

from packaging.version import Version

from .hashing import Digest


@dataclass(frozen=True)
class Science:
    @classmethod
    def spec(cls, version: str, digest: Digest | None = None) -> Science:
        return cls(version=Version(version), digest=digest)

    version: Version | None = None
    digest: Digest | None = None


class Url(str):
    @cached_property
    def info(self):
        return urllib.parse.urlparse(self)
