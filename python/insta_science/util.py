# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from typing import Any

from ._colors import color_support


def main() -> Any:
    with color_support() as colors:
        raise NotImplementedError(
            colors.yellow(
                "TODO(John Sirois): implement download subcommand for seeding offline `science` "
                "binary access."
            )
        )
