# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import os
from dataclasses import dataclass
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Any

from .errors import InputError, InvalidProjectError

try:
    import tomllib as toml  # type: ignore[import-not-found]
    from tomllib import TOMLDecodeError as TOMLError  # type: ignore[import-not-found]
except ImportError:
    import tomli as toml  # type: ignore[import-not-found,no-redef]
    from tomli import (  # type: ignore[import-not-found,no-redef,assignment]
        TOMLDecodeError as TOMLError,
    )


@dataclass(frozen=True)
class PyProjectToml:
    path: Path

    def parse(self) -> dict[str, Any]:
        try:
            with self.path.open("rb") as fp:
                return toml.load(fp)
        except (OSError, TOMLError) as e:
            raise InvalidProjectError(f"Failed to parse {self.path}: {e}")


def find_pyproject_toml() -> PyProjectToml | None:
    if pyproject_toml_str := os.environ.get("INSTA_SCIENCE_CONFIG"):
        custom_pyproject_toml = PyProjectToml(Path(pyproject_toml_str))
        if not custom_pyproject_toml.path.is_file():
            raise InputError(
                f"There is no pyproject.toml file at INSTA_SCIENCE_CONFIG={pyproject_toml_str}."
            )
        return custom_pyproject_toml

    module = Path(__file__)
    start = module.parent
    try:
        dist_files = metadata.files("insta-science")
        if dist_files and any(module == dist_file.locate() for dist_file in dist_files):
            # N.B.: We're running from an installed package; so use the PWD as the search start.
            start = Path()
    except PackageNotFoundError:
        # N.B.: We're being run directly from sources that are not installed or are installed in
        # editable mode.
        pass

    candidate = start.resolve()
    while True:
        pyproject_toml = candidate / "pyproject.toml"
        if pyproject_toml.is_file():
            return PyProjectToml(pyproject_toml)
        if candidate.parent == candidate:
            break
        candidate = candidate.parent

    return None
