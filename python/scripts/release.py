# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError
from textwrap import dedent
from typing import Any, Iterable, TextIO

import colors
import marko
from marko.block import Heading
from marko.element import Element
from marko.inline import RawText
from marko.md_renderer import MarkdownRenderer
from packaging.version import Version

from insta_science import __version__

REMOTE = "https://github.com/a-scie/science-installers"
RELEASE_BRANCH = "main"

VERSION = Version(__version__)
RELEASE_TAG = f"python-v{__version__}"

CHANGELOG = Path("CHANGES.md")
RELEASE_HEADING_LEVEL = 2


@dataclass(frozen=True)
class Release:
    version: Version
    elements: Iterable[Element]

    def render(self, output: TextIO):
        with MarkdownRenderer() as renderer:
            for element in self.elements:
                output.write(renderer.render(element))


def extract_level_heading(element: Element, level: int) -> str | None:
    if (
        isinstance(element, Heading)
        and element.level == level
        and len(element.children) == 1
        and isinstance(element.children[0], RawText)
    ):
        return element.children[0].children
    return None


def parse_latest_release(changelog: str, level: int) -> Release | None:
    document = marko.parse(changelog)
    current_release: Version | None = None
    elements: list[Element] = []
    for child in document.children:
        heading = extract_level_heading(child, level)
        if heading is not None:
            if current_release is not None:
                return Release(version=current_release, elements=elements)
            current_release = Version(heading.strip())
            elements.append(child)
        elif current_release is not None:
            elements.append(child)
    return None


def branch() -> str:
    return subprocess.run(
        args=["git", "branch", "--show-current"], text=True, stdout=subprocess.PIPE, check=True
    ).stdout.strip()


def branch_status() -> str:
    return subprocess.run(
        args=["git", "--no-pager", "status", "--porcelain"],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    ).stdout.strip()


def release_tag_exists() -> str:
    subprocess.run(
        args=["git", "fetch", "--tags", REMOTE],
        capture_output=True,
        check=True,
    )
    process = subprocess.run(
        args=["git", "--no-pager", "log", "--decorate=full", "-1", "--stat", RELEASE_TAG],
        text=True,
        capture_output=True,
    )
    return process.stdout if process.returncode == 0 else ""


def tag_and_push_release() -> None:
    subprocess.run(
        args=["git", "tag", "--sign" "-a", "-m", f"Release {__version__}", RELEASE_TAG], check=True
    )
    subprocess.run(args=["git", "push", "--tags", REMOTE, "HEAD:main"], check=True)


def main() -> Any:
    if (current_branch := branch()) != RELEASE_BRANCH:
        return colors.yellow(
            f"Aborted release since the current branch is {current_branch} and releases must be "
            f"done from {RELEASE_BRANCH}."
        )

    if status := branch_status():
        print(status)
        print("---")
        return colors.yellow(
            "Aborted release since the current branch is dirty with the status shown above."
        )

    if existing_tag := release_tag_exists():
        print(existing_tag)
        print("---")
        return colors.yellow(
            f"Aborted release since there is already a release tag for {__version__} shown above."
        )

    release = parse_latest_release(CHANGELOG.read_text(), level=RELEASE_HEADING_LEVEL)
    if release is None or VERSION > release.version:
        heading = colors.red(f"There are no release notes for {__version__} in {CHANGELOG}!")
        return dedent(
            f"""\
            {heading}

            You need to add a level {RELEASE_HEADING_LEVEL} heading with the release version number
            followed by the release notes for that version.

            For example:
            ------------

            {'#' * RELEASE_HEADING_LEVEL} {__version__}

            These are the {__version__} release notes...
            """
        )
    elif VERSION < release.version:
        release.render(sys.stdout)
        print("---")
        return colors.red(
            f"The current version is {VERSION} which is older than the latest release of "
            f"{release.version} recorded in {CHANGELOG} and shown above."
        )

    release.render(sys.stdout)
    print("---")
    if (
        "y"
        != input("Do you want to proceed with releasing the changes above? [y|N]").strip().lower()
    ):
        return colors.yellow("Aborted release at user request.")

    tag_and_push_release()
    print(colors.green(f"Release {__version__} tagged and pushed."))
    print("You can view release progress by visiting the latest job here:")
    print("    https://github.com/a-scie/science-installers/actions/workflows/python-release.yml")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, CalledProcessError) as e:
        sys.exit(colors.red(str(e)))
