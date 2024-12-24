# Release Process

## Preparation

### Version Bump and Changelog

1. Bump the version in [`insta_science/version.py`](insta_science/version.py).
2. Run `uv run dev-cmd` as a sanity check on the state of the project.
3. Update [`CHANGES.md`](CHANGES.md) with any changes that are likely to be useful to consumers.
4. Open a PR with these changes and land it on https://github.com/a-scie/science-installers main.

## Release

Before you can release, you'll first need to get on your local main branch and sync it with
https://github.com/a-scie/science-installers main. After that you can proceed using either the
semi-automated release tooling or manually. Each technique is described below.

Whichever technique you use, the final steps are automated by the [Python Release](
../.github/workflows/python-release.yml) action which will create a PyPI release at
[https://pypi.org/project/insta-science/&lt;version&gt;/](
https://pypi.org/project/insta-science/#history).

### Semi Automated

Just run `uv run dev-cmd release`. You should see output similar to the output below if you've
done a version bump and CHANGES.md edit as described above:
```
$ uv run dev-cmd release
dev run release] Executing release...
## 0.2.0

Expose the `insta_science.ensure_installed` API for programmatic access
to the `science` binary's path.

---
Do you want to proceed with releasing the changes above? [y|N]
```

You must enter 'y' to confirm the release looks good.

### Manual

First confirm main has the version bump and changelog update as the tip commit:
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