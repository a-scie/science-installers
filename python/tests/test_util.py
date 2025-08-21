# Copyright 2024 Science project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from textwrap import dedent
from threading import Thread
from typing import Iterator

import pytest
from _pytest.monkeypatch import MonkeyPatch

from insta_science import Platform


@pytest.fixture(autouse=True)
def cache_dir(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("INSTA_SCIENCE_CACHE", str(cache_dir))
    return cache_dir


@dataclass(frozen=True)
class Server:
    port: int
    root: Path

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


@pytest.fixture
def server(tmp_path: Path) -> Iterator[Server]:
    serve_root = tmp_path / "http-root"
    serve_root.mkdir()

    # N.B.: Running Python in unbuffered mode here is critical to being able to read stdout.
    process = subprocess.Popen(
        args=[sys.executable, "-u", "-m", "http.server", "0"],
        cwd=serve_root,
        stdout=subprocess.PIPE,
    )
    try:
        port: Queue[int] = Queue()

        def read_data():
            try:
                data = process.stdout.readline()
                match = re.match(rb"^Serving HTTP on \S+ port (?P<port>\d+)\D", data)
                port.put(int(match.group("port")))
            finally:
                port.task_done()

        reader = Thread(target=read_data)
        reader.daemon = True
        reader.start()
        port.join()
        reader.join()

        yield Server(port=port.get(), root=serve_root)
    finally:
        process.kill()


def test_download_http_mirror(pyproject_toml: Path, server: Server) -> None:
    pyproject_toml.write_text(
        dedent(
            f"""\
            [tool.insta-science.science]
            version = "0.13.0"
            base-url = "{server.url}"
            """
        )
    )

    subprocess.run(args=["insta-science-util", "download", server.root], check=True)
    subprocess.run(args=["insta-science", "-V"], check=True)


def test_download_file_mirror(pyproject_toml: Path, tmp_path: Path) -> None:
    mirror_dir = tmp_path / "mirror"
    mirror_url = f"file:{'///' if Platform.current().is_windows else '//'}{mirror_dir.as_posix()}"
    pyproject_toml.write_text(
        dedent(
            f"""\
            [tool.insta-science.science]
            version = "0.13.0"
            base-url = "{mirror_url}"
            """
        )
    )

    subprocess.run(args=["insta-science-util", "download", mirror_dir], check=True)
    subprocess.run(args=["insta-science", "-V"], check=True)
