# Science Installers

This project is home to installers and shims for the science binary that help make it more
convenient to bootstrap and work with in various interpreter ecosystems.

Each ecosystem supported has a top-level directory named after that ecosystem. For example,
the `python/` directory contains a Python project distributed on PyPI that provides an
`inst-science` console script shim that ensures science is installed and forwards all arguments to
it.

For more information about the installers and shims available for an ecosystem, check out the
`README.md` in its directory.