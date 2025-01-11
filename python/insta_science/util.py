# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import errno
import hashlib
import io
import os
import shutil
import sys
import uuid
from argparse import ArgumentParser, Namespace
from pathlib import Path, PurePath
from typing import Any

from packaging.version import Version

from . import CURRENT_PLATFORM, InputError, Platform, Science, __version__
from ._internal import a_scie, parser, project, science
from ._internal.bytes import ByteAmount
from ._internal.cache import DownloadCache, download_cache
from ._internal.colors import Colors, color_support
from ._internal.du import DiskUsage
from ._internal.model import Configuration


def download(
    options: Namespace, configuration: Configuration, cache: DownloadCache, _: Colors
) -> Any:
    dest = options.dest[0]
    versions = options.versions or [configuration.science.version]
    platforms = options.platforms or [CURRENT_PLATFORM]

    for version in versions:
        if version:
            dest_dir = dest / "download" / f"v{version}"
        else:
            dest_dir = dest / "latest" / "download"
        dest_dir.mkdir(parents=True, exist_ok=True)

        for platform in platforms:
            binary_name = platform.qualified_binary_name("science-fat")
            dest = dest_dir / binary_name
            print(f"Downloading science {version or 'latest'} for {platform} to {dest}...")
            science_exe = a_scie.science(cache, spec=Science(version=version), platform=platform)
            digest = hashlib.sha256()
            with open(science_exe.path, "rb") as read_fp, open(dest, "wb") as write_fp:
                for chunk in iter(lambda: read_fp.read(io.DEFAULT_BUFFER_SIZE), b""):
                    write_fp.write(chunk)
                    digest.update(chunk)
            shutil.copymode(science_exe.path, dest)
            (dest_dir / f"{binary_name}.sha256").write_text(f"{digest.hexdigest()} *{binary_name}")


def cache_prune(
    _: Namespace, configuration: Configuration, cache: DownloadCache, colors: Colors
) -> Any:
    retain_version = configuration.science.version
    original_du = cache.usage()

    cached: list[tuple[PurePath, Version | None]] = []
    for science_exe in science.iter_science_exes(cache):
        version_or_error = science_exe.version()
        cached.append(
            (science_exe.path, version_or_error if isinstance(version_or_error, Version) else None)
        )

    pruned: list[tuple[PurePath, Version | None]] = []
    retained: tuple[PurePath, Version | None] | None = None
    if retain_version:
        for path, version in cached:
            if version == retain_version:
                retained = path, version
                continue
            os.unlink(path)
            pruned.append((path, version))
    elif science_exes := sorted(cached, key=lambda tup: tup[1] or Version("0")):
        retained = science_exes[-1]
        for path, version in science_exes[:-1]:
            os.unlink(path)
            pruned.append((path, version))

    for pruned_exe, version in pruned:
        label = f"science {version}" if version else "foreign science binary"
        print(f"Pruned {label} ({colors.gray(f'at {pruned_exe}')}).")

    if retained:
        path, version = retained
        print(f"{colors.green(f'Retained science {version}')} ({colors.gray(f'at {path}')}).")
    elif retain_version:
        print(f"Configured to use science {retain_version} but that version is not cached.")

    if pruned:
        freed = ByteAmount.human_readable(original_du.size - cache.usage().size)
        print(
            f"{colors.green('Cache pruned. Freed')} "
            f"{colors.color(freed, fg='green', style='bold')}."
        )
    else:
        print("No cache entries were pruned.")


def cache_purge(_: Namespace, __: Configuration, cache: DownloadCache, colors: Colors) -> Any:
    atomic = f"{cache.base_dir}.{uuid.uuid4().hex}"
    try:
        os.rename(cache.base_dir, atomic)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return (
                f"Nothing to do ({colors.gray(f'cache not yet established at {cache.base_dir}')})."
            )
        return colors.red(f"Failed to re-name cache dir for pruning: {e}")

    du = DiskUsage.collect(atomic)
    shutil.rmtree(atomic, ignore_errors=True)
    print(
        f"{colors.green('Cache purged. Freed')} "
        f"{colors.color(ByteAmount.human_readable(du.size), fg='green', style='bold')}."
    )


def main() -> Any:
    argument_parser = ArgumentParser(description="Utilities for working with insta-science.")
    argument_parser.add_argument("-V", "--version", action="version", version=__version__)
    argument_parser.add_argument(
        "--cache-dir", type=PurePath, help="A custom cache directory to use."
    )

    sub_parsers = argument_parser.add_subparsers()
    download_parser_help = "Download science binaries for offline use."
    download_parser = sub_parsers.add_parser(
        "download", help=download_parser_help, description=download_parser_help
    )
    download_parser.add_argument(
        "dest",
        nargs=1,
        type=Path,
        metavar="DOWNLOAD_DIR",
        help="The directory to download science executables to",
    )
    download_parser.add_argument(
        "--version",
        dest="versions",
        action="append",
        type=Version,
        metavar="VERSION",
        help=(
            "One or more science versions to download. By default the "
            "[tools.insta-science.science] `version` is used if configured; otherwise the latest "
            "release is downloaded."
        ),
    )
    platforms_group = download_parser.add_mutually_exclusive_group()
    platforms_group.add_argument(
        "--all-platforms",
        dest="platforms",
        action="store_const",
        const=list(Platform),
        help=(
            "Download science binaries for all platforms science supports. Mutually exclusive "
            "with `--platform`. By default, only binaries for the current platform are downloaded."
        ),
    )
    platforms_group.add_argument(
        "--platform",
        dest="platforms",
        action="append",
        type=Platform,
        choices=list(Platform),
        help=(
            "Download science binaries for the specified platform(s). Mutually exclusive with "
            "`--platform`. By default, only binaries for the current platform are downloaded."
        ),
    )
    download_parser.set_defaults(func=download)

    cache_parser_help = "Manage the insta-science cache."
    cache_parser = sub_parsers.add_parser(
        "cache", help=cache_parser_help, description=cache_parser_help
    )
    cache_parsers = cache_parser.add_subparsers()

    prune_parser_help = "Prune any unused science binaries from the cache."
    prune_parser = cache_parsers.add_parser(
        "prune", help=prune_parser_help, description=prune_parser_help
    )
    prune_parser.set_defaults(func=cache_prune)

    purge_parser_help = "Purge the cache completely."
    purge_parser = cache_parsers.add_parser(
        "purge", help=purge_parser_help, description=purge_parser_help
    )
    purge_parser.set_defaults(func=cache_purge)

    options = argument_parser.parse_args()

    pyproject_toml = project.find_pyproject_toml()
    configuration = (
        parser.parse_configuration(pyproject_toml) if pyproject_toml else Configuration()
    )

    cache = download_cache(cache_dir=options.cache_dir or configuration.cache)
    with color_support() as colors:
        if func := getattr(options, "func", None):
            try:
                sys.exit(func(options, configuration, cache, colors))
            except InputError as e:
                sys.exit(f"{colors.red('Configuration error')}: {colors.yellow(str(e))}")
        argument_parser.print_help()
