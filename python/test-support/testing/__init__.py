# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import os
from pathlib import PurePath

from insta_science import CURRENT_PLATFORM


def is_exe(path: PurePath) -> bool:
    if not os.path.isfile(path):
        return False
    if CURRENT_PLATFORM.is_windows:
        return True
    return os.access(path, os.R_OK | os.X_OK)
