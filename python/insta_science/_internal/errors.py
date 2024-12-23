# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).


class InputError(ValueError):
    """An error caused by bad input.

    These errors are discriminated by the main application as containing error information bound
    for a user who may have supplied bad input that they can correct or may be running the
    application in a bad environmental setup that they can correct.

    By default, backtraces will not be displayed for these exceptions since they are not
    exceptional cases; they're anticipated errors.
    """


class InvalidProjectError(InputError):
    """Indicates bad pyproject.toml configuration for `[tool.insta-science]`."""


class ScienceNotFound(Exception):
    """Indicates the science binary could not be found.

    This generally means there was an error downloading a science binary.
    """
