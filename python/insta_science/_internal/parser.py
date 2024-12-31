# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import os.path
from pathlib import PurePath
from typing import Any, cast

from packaging.version import InvalidVersion, Version

from .errors import InputError
from .hashing import Digest, Fingerprint
from .model import Configuration, Science, Url
from .project import PyProjectToml


def _assert_dict_str_keys(obj: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(obj, dict) or not all(isinstance(key, str) for key in obj):
        raise InputError(
            f"Expected value at {path} to be a dict with string keys, but given: {obj} of type "
            f"{type(obj)}."
        )
    return cast("dict[str, Any]", obj)


def parse_configuration(pyproject_toml: PyProjectToml) -> Configuration:
    pyproject_data = pyproject_toml.parse()
    try:
        insta_science_data = _assert_dict_str_keys(
            pyproject_data["tool"]["insta-science"], path="[tool.insta-science]"
        )
    except KeyError:
        return Configuration()

    science_data = _assert_dict_str_keys(
        insta_science_data.pop("science", {}), path="[tool.insta-science.science]"
    )

    version: Version | None = None
    version_str = science_data.pop("version", None)
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
        science_data.pop("digest", {}), path="[tool.insta-science.science.digest]"
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

    base_url: Url | None = None
    base_url_str = science_data.pop("base-url", None)
    if base_url_str:
        if not isinstance(base_url_str, str):
            raise InputError(
                f"The [tool.insta-science.science] `base-url` value should be a string; given: "
                f"{base_url_str} of type {type(base_url_str)}."
            )
        base_url = Url(base_url_str)

    if science_data:
        raise InputError(
            f"Unexpected configuration keys in the [tool.insta-science.science] table: "
            f"{' '.join(science_data)}"
        )

    if digest and not version:
        raise InputError(
            "A [tool.insta-science.science.digest] can only be specified if "
            "[tool.insta-science.science] `version` is set."
        )

    cache_str = insta_science_data.pop("cache", None)
    if cache_str and not isinstance(cache_str, str):
        raise InputError(
            f"The [tool.insta-science] `cache` value should be a string; given: {cache_str} of "
            f"type {type(cache_str)}."
        )

    if insta_science_data:
        raise InputError(
            f"Unexpected configuration keys in the [tool.insta-science] table: "
            f"{' '.join(insta_science_data)}"
        )

    return Configuration(
        science=(
            Science(version=version, digest=digest, base_url=base_url)
            if base_url
            else Science(version=version, digest=digest)
        ),
        cache=PurePath(os.path.expanduser(cache_str)) if cache_str else None,
    )
