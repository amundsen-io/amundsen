# Maintaining Amundsen

As maintainers of the project, this is our guide. Most of the steps and guidelines in the [Contributing](CONTRIBUTING.md) document apply here, including how to set up your environment, write code to fit the code style, run tests, craft commits and manage branches.

Beyond this, this document provides some details that would be too low-level for contributors.

## Table of Contents

- [Communication](#communication)
- [Managing the community](#managing-the-community)
- [Issue management](#issue-management)
- [Dev workflow](#dev-workflow)
- [Architecture](#architecture)
- [Updating the changelog](#updating-the-changelog)
- [Documentation](#documentation)
- [Adding new projects](#adding-new-projects)
- [Related Documents](#related-documents)

## Communication

We have several ways that we can communicate with each other:

- To show our direction and next steps, the [**roadmap**][roadmap] is the best place.
- To track progress on the movement of issues, [**labels**](#labels) are useful.
- To learn about what the community has been working lately, our [community meeting] is a great event. It happens the first Thursday of every month at 9AM PST, and you can watch past meeting recordings [here][cmeetingrecordings]
- To chat with the maintainers team, get support or connect with Amundsen's community, join our [Slack][slack]

[roadmap]: https://www.amundsen.io/amundsen/roadmap/
[cmeeting]: meet.google.com/mqz-ndck-jmj
[cmeetingrecordings]: https://www.youtube.com/channel/UCgOyzG0sEoolxuC9YXDYPeg
[slack]: amundsenworkspace.slack.com

## Managing the community

We try to create and foster a community around Amundsen. We do this by:

- Answering questions from members of the community
- Triaging Github issues, adding the proper [labels][labels] to new tickets
- Keeping the community informed by ensuring that we add communications regularly with the new features
- Ensuring that the documentation, as well as the documentation site, is kept up to date
- Doing code reviews for other maintainers and the community
- Reviewing [RFCs][rfcs] and shaping the future of the project

[labels]: https://github.com/amundsen-io/amundsen/labels
[rfcs]: https://github.com/amundsen-io/rfcs


## Issue management

The triage and issue managing process will look like this:

1. New issues will automatically added the "Status: Needs Triage".
2. Once maintainers review the issue, they will remove the "Status: Needs Triage" label, add new ones and close the issue.
3. The Amundsen community will upvote the issues they want to be addressed by viewing the [features](https://github.com/amundsen-io/amundsen/issues?q=is%3Aissue+is%3Aclosed+sort%3Areactions-%2B1-desc+label%3Atype%3Afeature+) and [bug](https://github.com/amundsen-io/amundsen/issues?q=is%3Aissue+is%3Aclosed+sort%3Areactions-%2B1-desc+label%3Atype%3Abug+) lists and reacting with a 👍.
4. Amundsen maintainers and community will tackle the features and bugs as they fit their roadmap and taking into account their popularity.

We've found labels to be useful for cataloging and marking progress on features and bugs. You can read about our labels on the [issue_labeling](https://www.amundsen.io/amundsen/issue_labeling/) document.


## Dev workflow

We generally follow [GitHub Flow]. The `main` branch is the main line, and all
branches are cut from and get merged back into this branch. Generally, the
workflow is as follows:

[github flow]: https://help.github.com/articles/github-flow/

- Cut a feature or bugfix branch from this branch.
- Upon completing a branch, create a PR and ask another maintainer to approve it.
- Try to keep the commit history as clean as possible. Before merging, squash "WIP" or related commits together and rebase as needed.
- Once your PR is approved, and you've cleaned up your branch, you're free to merge it in.

## Architecture

We have covered Amundsen's architecture in our [docs](https://lyft.github.io/amundsen/architecture/).

## Documentation

We use [mkdocs] for creating our documentation from Markdown files. This system is configured from the 'mkdocs.yml' file in the root of this repository.

Currently, our docs are built and deployed automatically with a GitHub action, so we shouldn't need to do anything.

[mkdocs]: https://www.mkdocs.org/

## Adding new projects

To add new projects to the amundsen-io organization, we will first discuss it through our [RFC process][rfc].

[rfc]: https://github.com/amundsen-io/rfcs

## Related Documents

- [Contributing Guide](https://www.amundsen.io/amundsen/CONTRIBUTING/)
- [Governance Document](https://github.com/amundsen-io/amundsen/blob/master/GOVERNANCE.md)
