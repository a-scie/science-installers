# insta-science

[![PyPI Version](https://shields.io/pypi/v/insta-science.svg)](https://pypi.org/project/insta-science/)
[![License](https://shields.io/pypi/l/insta-science.svg)](../LICENSE)
[![Supported Pythons](https://shields.io/pypi/pyversions/insta-science.svg)](pyproject.toml)
[![CI](https://img.shields.io/github/actions/workflow/status/a-scie/science-installers/python-ci.yml)](https://github.com/a-scie/science-installers/actions/workflows/python-ci.yml)

The `insta-science` Python project distribution provides two convenience console scripts to make
bootstrapping `science` for use in Python projects easier:
+ `insta-science`: This is a shim script that ensures `science` is installed and then forwards all
  supplied arguments to it. Instead of `science`, just use `insta-science`. You can configure the
  `science` version to use, where to find `science` binaries and where to install them via the 
  `[tool.insta-science]` table in your `pyproject.toml` file.
+ `insta-science-util`: This script provides utilities for managing `science` binaries. In
  particular, it supports downloading families of `science` binaries for various platforms for
  use in internal serving systems for offline or isolated installation.

This project is under active early development and APIs and configuration are likely to change
rapidly in breaking ways until the 1.0 release.

## Configuration

By default, `insta-science` downloads the latest science binary release appropriate for the current
platform from the `science` [GitHub Releases](https://github.com/a-scie/lift/releases) and caches it
before executing for the 1st time. You can control aspects of this process using the
`[tool.insta-science]` table in your `pyproject.toml` file. Available configuration options are
detailed below:

| Option             | Default                                   | `pyproject.toml` entry                  | Environment Variable  |
|--------------------|-------------------------------------------|-----------------------------------------|-----------------------|
| `science` version  | latest                                    | [tool.insta-science.science] `version`  |                       |
| `science` Base URL | https://github.com/a-scie/lift/releases   | [tool.insta-science.science] `base-url` |                       |
| Cache directory    | Unix:    `~/.cache/insta-science`         | [tool.insta-science] `cache`            | `INSTA_SCIENCE_CACHE` |
|                    | Mac:     `~/Library/Caches/insta-science` |                                         |                       |
|                    | Windows: `~\AppData\Local\insta-science`  |                                         |                       |

## Offline Use

There is partial support for offline or firewalled `science` use with `insta-science`. You can seed
a repository of science binaries by using the `insta-science-util download` command to download
`science` binaries for one or more versions and one or more target platforms. The directory you
download these binaries to will have the appropriate structure for `insta-science` to use if you
serve up that directory using your method of choice at the configured base url.

Full offline use requires similar support in `science` for downloading offline copies of the
[`scie-jump` binaries](https://github.com/a-scie/jump/releases), [`ptex` binaries](
https://github.com/a-scie/ptex/releases) and interpreter provider provided archives; e.g.
[PythonBuildStandalone](https://science.scie.app/_/providers/PythonBuildStandalone.html)
distributions. That support is tracked in [science issue #114](https://github.com/a-scie/lift/issues/114).

## Development

Development uses [`uv`](https://docs.astral.sh/uv/getting-started/installation/). Install as you
best see fit.

With `uv` installed, running `uv run dev-cmd` is enough to get the tools insta-science uses
installed and run against the codebase. This includes formatting code, linting code, performing type
checks and then running tests.
