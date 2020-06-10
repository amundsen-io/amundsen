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
We describe our [general contributing process](https://lyft.github.io/amundsen/CONTRIBUTING/) in the main repository of Amundsen, so here we'll cover the items specific to the Frontend library.

### Testing Python Code
If changes were made to any python files, run the python unit tests, linter, and type checker. Unit tests are run with `py.test`. They are located in `tests/unit`. Type checks are run with `mypy`. Linting is `flake8`. There are friendly `make` targets for each of these tests:
```bash
# after setting up the environment
make test  # unit tests in Python 3
make lint  # flake8
make mypy  # type checks
```
Fix all errors before submitting a PR.

### Testing Frontend Code
`npm run test` runs our Frontend unit tests. Please add unit tests to cover new code additions and fix any test failures before submitting a PR. You can also have a dedicated terminal running `npm run test:watch` while developing, which would continuously run tests over your modified files.

To run specific tests, run `npm run test-nocov -t <regex>`, where `<regex>` is any pattern that matches the names of the test blocks that you want to run. See our [recommendations for writing unit tests](https://github.com/lyft/amundsenfrontendlibrary/blob/master/docs/recommended_practices.md).

### Frontend Type Checking
We use TypeScript in our codebase, so `npm run tsc` conducts type checking. The build commands `npm run build` and `npm run dev-build` also conduct type checking, but are slower because they also build the source code. Run any of these commands and fix all failed checks before submitting a PR.

### Frontend Linting and Formatting
We have in place two linters – [ESLint][eslint] for our JavaScript and TypeScript files, [Stylelint][stylelint] for our Sass files. If you have both ESLint and Stylelint extensions installed on your IDE, you should get warnings on your editor by default.

We also use [Prettier][prettier] to help us keep consistent formatting on our TypeScript and Sass code.

Whenever you want to run these tasks manually, you can execute:

* `npm run lint` to run ESLint and `npm run lint-fix` to auto-fix most of them.
* `npm run stylelint` to run Stylelint and `npm run stylelint-fix` to trigger the auto-fix.
* `npm run format` to run Prettier on both the TypeScript and Sass files

We also check your changed files and format them when you create a new commit, making it easy for you and for the project to keep a consistent code style. We do this leveraging [Husky][husky] and [Lint-staged][lint-staged].

Looking forward, we aim at setting more strict best practices using ESLint and Stylelint. You can read about our plans to improve our TypeScript, Styles and general code style on these issues:
* [Adopt Typescript Recommended Guidelines on the Frontend library][typescript-issue]
* [Adopt Stylelint's Sass Guidelines on the Frontend library][stylelint-issue]
* [Adopt Airbnb-Typescript Code Guidelines on the Frontend library][airbnb-issue]

[eslint]: https://eslint.org/
[stylelint]: https://stylelint.io/
[prettier]: https://prettier.io/
[husky]: https://github.com/typicode/husky
[lint-staged]: https://github.com/okonet/lint-staged
[typescript-issue]: https://github.com/lyft/amundsen/issues/503
[airbnb-issue]: https://github.com/lyft/amundsen/issues/502
[stylelint-issue]: https://github.com/lyft/amundsen/issues/501


