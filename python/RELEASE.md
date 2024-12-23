# Release Process

## Preparation

### Version Bump and Changelog

1. Bump the version in [`insta_science/version.py`](insta_science/version.py).
2. Run `uv run dev-cmd` as a sanity check on the state of the project.
3. Update [`CHANGES.md`](CHANGES.md) with any changes that are likely to be useful to consumers.
4. Open a PR with these changes and land it on https://github.com/a-scie/science-installers main.

## Release

### Push Release Tag

Sync a local branch with https://github.com/a-scie/science-installers main and confirm it has the
version bump and changelog update as the tip commit:
```
$ git log --stat -1 HEAD | grep -E "CHANGES|__init__"
 python/CHANGES.md                    |   5 +
 python/insta_science/__init__.py     |   4 +```
```

Tag the release as `python-v<version>` and push the tag to
https://github.com/a-scie/science-installers main:
```
$ git tag --sign -am 'Release 0.1.0' python-v0.1.0
$ git push --tags https://github.com/a-scie/science-installers HEAD:main
```

The release is automated and will create a PyPI release at
[https://pypi.org/project/insta-science/&lt;version&gt;/](
https://pypi.org/project/insta-science/#history).
