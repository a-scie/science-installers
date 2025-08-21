# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import platform
import subprocess
from enum import Enum
from functools import lru_cache

from .errors import InputError


class Platform(Enum):
    Linux_aarch64 = "linux-aarch64"
    Linux_armv7l = "linux-armv7l"
    Linux_powerpc64le = "linux-powerpc64"
    Linux_riscv64 = "linux-riscv64"
    Linux_s390x = "linux-s390x"
    Linux_x86_64 = "linux-x86_64"
    Macos_aarch64 = "macos-aarch64"
    Macos_x86_64 = "macos-x86_64"
    Windows_aarch64 = "windows-aarch64"
    Windows_x86_64 = "windows-x86_64"

    @classmethod
    def current(cls) -> Platform:
        system = platform.system().lower()
        machine = platform.machine().lower()

        if "linux" == system:
            if machine in ("aarch64", "arm64"):
                return cls.Linux_aarch64
            elif machine in ("armv7l", "armv8l"):
                return cls.Linux_armv7l
            elif machine == "ppc64le":
                return cls.Linux_powerpc64le
            elif machine == "riscv64":
                return cls.Linux_riscv64
            elif machine == "s390x":
                return cls.Linux_s390x
            elif machine in ("amd64", "x86_64"):
                return cls.Linux_x86_64

        if "darwin" == system:
            if machine in ("aarch64", "arm64"):
                return cls.Macos_aarch64
            elif machine in ("amd64", "x86_64"):
                return cls.Macos_x86_64

        if "windows" == system:
            if machine in ("aarch64", "arm64"):
                return cls.Windows_aarch64
            elif machine in ("amd64", "x86_64"):
                return cls.Windows_x86_64

        raise InputError(
            f"The current operating system / machine pair is not supported!: {system} / {machine}"
        )

    @property
    def is_windows(self) -> bool:
        return self in (self.Windows_aarch64, self.Windows_x86_64)

    @property
    def extension(self) -> str:
        return ".exe" if self.is_windows else ""

    def binary_name(self, binary_name: str) -> str:
        return f"{binary_name}{self.extension}"

    def qualified_binary_name(self, binary_name: str, libc: LibC | None = None) -> str:
        platform_ = self.value
        if libc is LibC.MUSL and self is Platform.Linux_x86_64:
            platform_ = f"musl-{platform_}"
        return f"{binary_name}-{platform_}{self.extension}"

    def __str__(self) -> str:
        return self.value


CURRENT_PLATFORM = Platform.current()


class LibC(Enum):
    GLIBC = "gnu"
    MUSL = "musl"

    @classmethod
    @lru_cache(maxsize=None)
    def current(cls) -> LibC | None:
        if CURRENT_PLATFORM is not Platform.Linux_x86_64:
            return None
        result = subprocess.run(args=["ldd", "/bin/sh"], capture_output=True, text=True)
        return LibC.MUSL if result.returncode == 0 and "musl" in result.stdout else LibC.GLIBC

    def __str__(self) -> str:
        return self.value


CURRENT_LIBC = LibC.current()
