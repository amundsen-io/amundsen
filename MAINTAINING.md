# Maintaining Amundsen

As maintainers of the project, this is our guide. Most of the steps and guidelines
in the [Contributing](CONTRIBUTING.md) document apply here, including how to set
up your environment, write code to fit the code style, run tests, craft commits
and manage branches. Beyond this, this document provides some details that would
be too low-level for contributors.

## Table of Contents

- [Communication](#communication)
- [Managing the community](#managing-the-community)
- [Workflow](#workflow)
- [Architecture](#architecture)
- [Running tests](#running-tests)
- [Updating the changelog](#updating-the-changelog)
- [Documentation](#documentation)
- [Versioning](#versioning)
- [Releasing](#releasing)
- [Labels](#labels)

## Communication

We have several ways that we can communicate with each other:

- To show our direction and next steps, the [**roadmap**][roadmap] is the best place.
- To track progress on the movement of issues, [**labels**](#labels)
  are useful.
  TODO: Fill with the Slack community and the regular community meeting

[roadmap]: https://lyft.github.io/amundsen/roadmap/

## Managing the community

We try to create and foster a community around Amundsen. We do this by:

- Answering questions from members of the community
- Closing stale issues and feature requests
- Keeping the community informed by ensuring that we add communications regularly with the new features
- Ensuring that the documentation, as well as the documentation site, is kept up to
  date

## Workflow

We generally follow [GitHub Flow]. The `master` branch is the main line, and all
branches are cut from and get merged back into this branch. Generally, the
workflow is as follows:

[github flow]: https://help.github.com/articles/github-flow/

- Cut a feature or bugfix branch from this branch.
- Upon completing a branch, create a PR and ask another maintainer to approve
  it.
- Try to keep the commit history as clean as possible. Before merging, squash
  "WIP" or related commits together and rebase as needed.
- Once your PR is approved, and you've cleaned up your branch, you're free to
  merge it in.

## Architecture

TODO

## Running tests

TODO

## Updating the changelog

**TO ADOPT?**

After every user-facing change makes it into master, we make a note of it in the
changelog, `CHANGELOG.md`. The changelog is sorted in reverse order by release version.

Within each version, there are five available categories you can divide changes
into. They are all optional:

1. Deprecations
1. Bug fixes
1. Features
1. Enhancements

For each change, provide a human-readable description of the change.

## Documentation

We use [mkdocs] for creating our documentation from Markdown files. This system is configured
from the 'mkdocs.yml' file in the root of this repository.

Currently, our docs are built and deployed manually, so we should first build and deploy them locally and verify it. Here are some basic steps:

1. Activate the virtualenv with `source venv/bin/activate`
1. Install the requirements: `pip3 install -r requirements.txt`
1. Install mkdocs with Homebrew (Mac only): `brew install mkdocs`
1. Create the documentation with `mkdocs serve` navigate to them in localhost:8000. On mac OS, you may face ImportError and you may need to downgrade openssl by running `brew switch openssl 1.0.2r`
1. Deploy our docs to the Github pages using `mkdocs gh-deploy`

[mkdocs]: https://www.mkdocs.org/

## Versioning

### Naming a new version

**TO REVIEW**

We follow [SemVer 2.0][semver]. This offers a meaningful baseline for deciding how to name versions. Generally speaking:

[semver]: https://semver.org/spec/v2.0.0.html

- We bump the "major" part of the version if we're introducing
  backward-incompatible changes (e.g., changing the API or core behavior,
  removing parts of the API).
- We bump the "minor" part if we're adding a new feature.
- We bump the "patch" part if we merely include bugfixes.

In addition to major, minor, and patch levels, you can also append a
suffix to the version for pre-release versions. We usually use this to issue
release candidates prior to an actual release.

### Preparing and releasing a new version

**TO REVIEW**

Assuming you have permission to publish a new version of Amundsen, then this is
how you release a version:

1. First, you'll want to [make sure that the changelog is up to
   date](#updating-the-changelog).

2. Next, [generate the documentation locally](#documentation) and do
   a quick spot-check to ensure that nothing looks awry.

3. Next, you'll want to update the `VERSION` constant in \*\*.

4. ...

## Labels

We've found labels to be useful for cataloging and marking progress on features and bugs. You can read about our labels on the [issue_labeling](https://lyft.github.io/amundsen/issue_labeling/) document.
