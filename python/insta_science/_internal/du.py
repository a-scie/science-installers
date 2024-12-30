# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import itertools
import os
import stat
from dataclasses import dataclass
from pathlib import PurePath
from typing import Iterable


@dataclass(frozen=True)
class DiskUsage(object):
    @classmethod
    def aggregate(cls, path: str, usages: Iterable[DiskUsage]) -> DiskUsage:
        subdirs = 0
        files = 0
        size = 0
        for disk_usage in usages:
            subdirs += disk_usage.subdirs
            files += disk_usage.files
            size += disk_usage.size
        return cls(path=PurePath(path), subdirs=subdirs, files=files, size=size)

    @classmethod
    def collect(cls, path: str) -> DiskUsage:
        """Collects data with the same default semantics as `du`.

        Does not count directory inode sizes.
        Only counts hard linked file sizes once.
        Counts symlink size as the size of the target path string not including the null terminator.
        """
        subdir_count = 0
        file_count = 0
        size = 0
        seen: set[int] = set()
        for root, dirs, files in os.walk(path):
            for f in itertools.chain(dirs, files):
                stat_info = os.lstat(os.path.join(root, f))
                if stat_info.st_ino in seen:
                    continue
                seen.add(stat_info.st_ino)
                if stat.S_ISDIR(stat_info.st_mode):
                    subdir_count += 1
                else:
                    file_count += 1
                    size += stat_info.st_size

        return cls(path=PurePath(path), subdirs=subdir_count, files=file_count, size=size)

    path: PurePath
    subdirs: int
    files: int
    size: int
