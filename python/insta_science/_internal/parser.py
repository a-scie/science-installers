# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from typing import Any, cast

from packaging.version import InvalidVersion, Version

from .errors import InputError
from .hashing import Digest, Fingerprint
from .model import Science
from .project import PyProjectToml


def _assert_dict_str_keys(obj: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(obj, dict) or not all(isinstance(key, str) for key in obj):
        raise InputError(
            f"Expected value at {path} to be a dict with string keys, but given: {obj} of type "
            f"{type(obj)}."
        )
    return cast("dict[str, Any]", obj)


def configured_science(pyproject_toml: PyProjectToml) -> Science:
    pyproject_data = pyproject_toml.parse()
    try:
        insta_science_data = _assert_dict_str_keys(
            pyproject_data["tool"]["insta-science"]["science"], path="[tool.insta-science.science]"
        )
    except KeyError:
        return Science()

    version: Version | None = None
    version_str = insta_science_data.pop("version", None)
    if version_str:
        if not isinstance(version_str, str):
            raise InputError(
                f"The [tool.insta-science.science] `version` value should be a string; given: "
                f"{version_str} of type {type(version_str)}."
            )
        try:
            version = Version(version_str)
        except InvalidVersion:
            raise InputError(
                f"The [tool.insta-science.science] `version` should be in X.Y.Z form; given: "
                f"{version_str}"
            )

    digest: Digest | None = None
    digest_data = _assert_dict_str_keys(
        insta_science_data.pop("digest", {}), path="[tool.insta-science.science.digest]"
    )
    if digest_data:
        try:
            size = digest_data.pop("size")
        except KeyError:
            raise InputError(
                "When specifying a [tool.insta-science.science.digest] table, the `size` key is "
                "required. "
            )
        if not isinstance(size, int):
            raise InputError(
                f"The [tool.insta-science.science.digest] `size` value should be an integer; "
                f"given: {size} of type {type(size)}."
            )

        try:
            fingerprint = digest_data.pop("fingerprint")
        except KeyError:
            raise InputError(
                "When specifying a [tool.insta-science.science.digest] table, the `fingerprint` "
                "key is required. "
            )
        if not isinstance(fingerprint, str):
            raise InputError(
                f"The [tool.insta-science.science.digest] `fingerprint` value should be a string; "
                f"given: {fingerprint} of type {type(fingerprint)}."
            )

        if digest_data:
            raise InputError(
                f"Unexpected configuration keys in the [tool.insta-science.science.digest] table: "
                f"{' '.join(digest_data)}"
            )

        digest = Digest(size, fingerprint=Fingerprint(fingerprint))

    if insta_science_data:
        raise InputError(
            f"Unexpected configuration keys in the [tool.insta-science.science] table: "
            f"{' '.join(insta_science_data)}"
        )

    if digest and not version:
        raise InputError(
            "A [tool.insta-science.science.digest] can only be specified if "
            "[tool.insta-science.science] `version` is set."
        )

    return Science(version=version, digest=digest)
