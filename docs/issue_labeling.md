# Issue and Feature Labeling
> On Amundsen, we aim to be methodical on using issue labels, offering our community a way to understand what are the issues about and their status within or development process.

We use a bunch of GitHub labels. They are a mix of custom labels and the default Github labels for open-source projects. We base these labels on four main types: **status labels**, **issue type labels**, **area labels**, and the **“other” category**. Read on to learn more about them.

## Status Labels
* They show at a glance the status and progress of each issue
* Prefixed with "Status:", followed by the label
* Only *one status label* will be applied to any particular issue

### Labels
- **status:needs_triage** – For all issues that need to be processed
- **status:needs_reproducing** – For bugs that need to be reproduced in order to get fixed
- **status:needs_votes** – Issue or bug fix that needs support from the community to be considered
- **status:in_progress** – Issue that is being worked on right now.
- **status:completed** – Issue is completed and on main
- **status:abandoned** – Issue we won’t go ahead and implement, or that needs a “champion” to take it through
- **status:blocked** – Issue blocked by any reason (dependencies, previous work, lack of resources, etc.)

Here is a diagram representing these states within the lifecycles:
![Feature and Bug Lifecycle](https://raw.githubusercontent.com/amundsen-io/amundsen/main/docs/img/process/issue_process_diagram.png)

## Type Labels
* They show the type of the issue
* Prefixed with "Type:", followed by the label

### Labels
- **type:bug** – An unexpected problem or unintended behavior
- **type:feature** – A new feature request
- **type:maintenance** – A regular maintenance chore or task, including refactors, build system, CI, performance improvements
- **type:documentation** – A documentation improvement task
- **type:question** – An issue or PR that needs more information or a user question

## Area Labels
* They indicate which area of the project the issue refers to
* Prefixed with "Area:", followed by the name of the project

### Labels
- **area:common** – From common
- **area:databuilder** – From databuilder
- **area:frontend** – From frontend
- **area:metadata** – From metadata library
- **area:search** – From search library
- **area:k8s** – Related to the Kubernetes helm chart
- **area:all** – Related to all the projects above

## Other Labels
* Some of these are part of the standard GitHub labels and intended for OSS contributors
* Some are related to the tools we use to maintain the library
* They are not prefixed

### Labels
- **help wanted** – Indicates we are looking for contributors on this issue.
- **good first issue** – Indicates the issue is a great one to tackle by newcomers to the project or OSS in general.
- **rfc** - Indicates that there is an RFC associated with this issue.
