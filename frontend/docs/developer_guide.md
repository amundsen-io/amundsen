# Developer Guide

## Environment
Follow the installation instructions in the section [Install standalone application directly from the source](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docs/installation.md#install-standalone-application-directly-from-the-source).

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

### Testing
#### Python

If changes were made to any python files, run the python unit tests, linter, and type checker. Unit tests are run with `py.test`. They are located in `tests/unit`. Type checks are run with `mypy`. Linting is `flake8`. There are friendly `make` targets for each of these tests:
```bash
# after setting up environment
make test  # unit tests in Python 3
make lint  # flake8
make mypy  # type checks
```
Fix all errors before submitting a PR.

#### JS Assets

##### Type Checking
`npm run tsc` conducts type checking. The build commands `npm run build` and `npm run dev-build` also conduct type checking, but are slower because they also build the source code. Run any of these commands and fix all failed checks before submitting a PR.

##### Lint
`npm run lint` runs the linter. Fix all lint errors before submitting a PR. `npm run lint-fix` can help auto-fix most common errors.

##### Unit Tests
`npm run test` runs unit tests. Add unit tests to cover new code additions and fix any test failures before submitting a PR.

To run specific tests, run `npm run test-nocov -t <regex>`, where `<regex>` is any pattern that matches the names of the test blocks that you want to run.

See our recommendations for writing unit tests [here](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docs/recommended_practices.md).
