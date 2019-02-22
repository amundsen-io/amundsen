# Developer Guide

## Environment
Follow the installation instructions in the section [Install standalone application directly from the source](https://github.com/lyft/amundsenfrontendlibrary#install-standalone-application-directly-from-the-spource).

Install the javascript development requirements:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/amundsen_application
$ cd static
$ npm install --only=dev
```

To test local changes to the javascript static files:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/amundsen_application
$ cd static
$ npm run dev-build # builds the development bundle
```

To test local changes to the python files, re-run the wsgi:
```bash
# in ~/<your-path-to-cloned-repo>/amundsenfrontendlibrary/amundsen_application
$ python3 wsgi.py
```

## Contributing

### Python

If changes were made to any python files, run the python unit tests, linter, and type checker. Unit tests are run with `py.test`. They are located in `tests/unit`. Type checks are run with `mypy`. Linting is `flake8`. There are friendly `make` targets for each of these tests:
```bash
# after setting up environment
make test  # unit tests in Python 3
make lint  # flake8
make mypy  # type checks
```
Fix all errors before submitting a PR.

### JS Assets
By default, the build commands that are run to verify local changes -- `npm run build` and `npm run dev-build` -- also conduct linting and type checking. During development be sure to fix all errors before submitting a PR.

**TODO: JS unit tests are in progress - document unit test instructions after work is complete**
