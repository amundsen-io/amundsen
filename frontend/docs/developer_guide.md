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

### Developing React Components

To preview React components in isolation, use [Storybook](https://storybook.js.org/). Just add a `<componentName>.story.tsx` file in the same folder as your component. In that file, show your component in different states. Then run `npm run storybook`, which will open your browser to the storybook browse page.

Using Storybook makes it much easier to quickly iterate on components when getting to certain states requires multiple steps of UI manipulation. The gallery also serves as a convenient place to see what reusable components are available so you can avoid reinventing the wheel.

### Frontend Type Checking

We use TypeScript in our codebase, so `npm run tsc` conducts type checking. The build commands `npm run build` and `npm run dev-build` also conduct type checking, but are slower because they also build the source code. Run any of these commands and fix all failed checks before submitting a PR.

### Frontend Linting and Formatting

We have in place two linters – [ESLint][eslint] for our JavaScript and TypeScript files, [Stylelint][stylelint] for our Sass files. If you have both ESLint and Stylelint extensions installed on your IDE, you should get warnings on your editor by default.

We also use [Prettier][prettier] to help us keep consistent formatting on our TypeScript and Sass code.

Whenever you want to run these tasks manually, you can execute:

- `npm run lint` to run ESLint and `npm run lint:fix` to auto-fix most of them.
- `npm run stylelint` to run Stylelint and `npm run stylelint:fix` to trigger the auto-fix.
- `npm run format` to run Prettier on both the TypeScript and Sass files

We also check your changed files and format them when you create a new commit, making it easy for you and for the project to keep a consistent code style. We do this leveraging [Husky][husky] and [Lint-staged][lint-staged].

Looking forward, we aim at setting more strict best practices using ESLint and Stylelint. For that, we are leveraging a project called [betterer][betterer], which keeps track of our errors when a given test is passed. You can run it using `npm run betterer` and it will break if you introduce any new eslint errors. If you want to ignore the new errors you can run `npm run betterer:update` to update the betterer.results file. We do not recommend adding or introducing new eslint errors.

You can read about our plans to improve our TypeScript, Styles and general code style on these issues:

- [Adopt Typescript Recommended Guidelines on the Frontend library][typescript-issue]
- [Adopt Stylelint's Sass Guidelines on the Frontend library][stylelint-issue]
- [Adopt Airbnb-Typescript Code Guidelines on the Frontend library][airbnb-issue]

### Accessibility and Semantic Markup

We strive to keep our application accessible. For that, we use the 'airbnb-typescript' preset for ESLint, which includes a bunch of accessibility rules. We also have a set of "jsx-a11y/" prefixed rules, which are currently on a "warn" level, so they don't throw errors. Our goal is to remove that "warn" level and comply with all the accessibility rules we list on [our ESLint configuration][eslintconfig].

We also try to model our application's markup on best practices regarding semantic markup. If you are making large markup changes on one of your PRs, make sure your changes comply with this [HTML semantics checklist][semanticchecklist].

### Typography

In the past, we have used several classes to set the styling of our heading and body text. Nowadays, we recommend to use classes in our stylesheets for each component, and extend those classes with the proper text styling by using an `@extend` to a placehoder selector:

```scss
@import "variables";
@import "typography";

.header-title-text {
  @extend %text-headline-w2;
}

.header-subtitle-text {
  @extend %text-subtitle-w3;
}
```

You can find the complete list of placeholder selectors for text in [this file](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/static/css/_typography-default.scss#L12). In the cases were a text class works best, you can use their equivalent classes.

[eslint]: https://eslint.org/
[eslintconfig]: https://github.com/lyft/amundsenfrontendlibrary/blob/master/amundsen_application/static/package.json#L242
[stylelint]: https://stylelint.io/
[prettier]: https://prettier.io/
[husky]: https://github.com/typicode/husky
[lint-staged]: https://github.com/okonet/lint-staged
[typescript-issue]: https://github.com/lyft/amundsen/issues/503
[airbnb-issue]: https://github.com/lyft/amundsen/issues/502
[stylelint-issue]: https://github.com/lyft/amundsen/issues/501
[semanticchecklist]: https://learn-the-web.algonquindesign.ca/topics/html-semantics-checklist/
[betterer]: https://github.com/phenomnomnominal/betterer
