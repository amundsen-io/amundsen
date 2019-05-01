Make sure you have checked **all** steps below.

### Title

- [ ] My PR Title addresses the issue accurately and concisely. 
    - Example: "Updates the version of Flask to v1.0.2"
    - In case you are adding a dependency, check if the license complies with the [ASF 3rd Party License Policy](https://www.apache.org/legal/resolved.html#category-x).

### Description

- [ ] Here are some details about my PR:

### Tests

- [ ] My PR adds the following unit tests __OR__ does not need testing for this extremely good reason:

### Commits

- [ ] I have squashed multiple commits if they address the same issue. In addition, my commits follow the guidelines from "[How to write a good git commit message](http://chris.beams.io/posts/git-commit/)":
    1. Subject is separated from body by a blank line
    1. Subject is limited to 50 characters (not including Jira issue reference)
    1. Subject does not end with a period
    1. Subject uses the imperative mood ("add", not "adding")
    1. Body wraps at 72 characters
    1. Body explains "what" and "why", not "how"

### Documentation

- [ ] In case of new functionality, my PR adds documentation that describes how to use it.
    - All the public functions and the classes in the PR contain docstrings that explain what it does

### Code Quality & Coverage

- [ ] Passes `make test`
