# insta-science

## 0.4.5

De-dup `insta-science-util download --platform` and fix its CLI help.

## 0.4.4

Use a 'User-Agent' header of `insta-science/<version>` when fetching URLs.

## 0.4.3

Implement proper HTTP error handling and add retry support in for failed `science` fetches.

## 0.4.2

Actually implement support for `[tool.insta-science] cache` configuration as claimed in the README.

## 0.4.1

Fix cache location on Windows and document `insta-science` configuration.

## 0.4.0

Flesh out the `insta-science-util` script adding support for downloading `science` executables for
offline serving in firewalled environments as well as support for managing the `insta-science`
cache.

## 0.3.1

Fix the semi-automated release process.

## 0.3.0

Add support for Python 3.8.

Also respect color settings when printing error output.

## 0.2.1

Fix the `insta_science.ensure_installed` API to not exit on error.

## 0.2.0

Expose the `insta_science.ensure_installed` API for programmatic access
to the `science` binary's path.

## 0.1.0

Initial release.
