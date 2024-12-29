# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import platform
from enum import Enum

from .errors import InputError


class Platform(Enum):
    Linux_aarch64 = "linux-aarch64"
    Linux_armv7l = "linux-armv7l"
    Linux_powerpc64le = "linux-powerpc64"
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
            f"The current operating system / machine pair is not supported!: "
            f"{system} / {machine}"
        )

    @property
    def is_windows(self) -> bool:
        return self in (self.Windows_aarch64, self.Windows_x86_64)

    @property
    def extension(self) -> str:
        return ".exe" if self.is_windows else ""

    def binary_name(self, binary_name: str) -> str:
        return f"{binary_name}{self.extension}"

    def qualified_binary_name(self, binary_name: str) -> str:
        return f"{binary_name}-{self.value}{self.extension}"


CURRENT_PLATFORM = Platform.current()
