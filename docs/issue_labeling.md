# Issue and Feature Labeling
> On Amundsen, we aim to be methodical on using issue labels, offering our community a way to understand what are the issues about and their status within or development process.

We use a bunch of GitHub labels. They are a mix of custom labels and the default Github labels for open-source projects. We base these labels on four main types: **status labels**, **issue type labels**, **area labels**, and the **“other” category**. Read on to learn more about them.

## Status Labels
* They show at a glance the status and progress of each issue
* Prefixed with "Status:", followed by the label
* Only *one status label* will be applied to any particular issue

### Labels
- **Status: Needs Triage** – For all issues that need to be processed
- **Status: Needs Reproducing** – For bugs that need to be reproduced in order to get fixed
- **Status: Needs Votes** – Issue or bug fix that needs support from the community to be considered
- **Status: In Progress** – Issue that is being worked on right now.
- **Status: Completed** – Issue is completed and on master
- **Status: Abandoned** – Issue we won’t go ahead and implement, or that needs a “champion” to take it through
- **Status: Blocked** – Issue blocked by any reason (dependencies, previous work, lack of resources, etc.)

Here is a diagram representing these states within the lifecycles:
![Feature and Bug Lifecycle](https://raw.githubusercontent.com/amundsen-io/amundsen/master/docs/img/process/issue_process_diagram.png)

## Type Labels
* They show the type of the issue
* Prefixed with "Type:", followed by the label

### Labels
- **Type: Bug** – An unexpected problem or unintended behavior
- **Type: Feature** – A new feature request
- **Type: Maintenance** – A regular maintenance chore or task, including refactors, build system, CI, performance improvements
- **Type: Documentation** – A documentation improvement task
- **Type: Question** – An issue or PR that needs more information or a user question

## Area Labels
* They indicate which area of the project the issue refers to
* Prefixed with "Area:", followed by the name of the project

### Labels
- **Area: Common** – From common
- **Area: Databuilder** – From databuilder
- **Area: Frontend** – From frontend
- **Area: Metadata** – From metadata library
- **Area: Search** – From search library
- **Area: k8s** – Related to the Kubernetes helm chart
- **Area: All** – Related to all the projects above

## Other Labels
* Some of these are part of the standard GitHub labels and intended for OSS contributors
* Some are related to the tools we use to maintain the library
* They are not prefixed

### Labels
- **help wanted** – Indicates we are looking for contributors on this issue.
- **good first issue** – Indicates the issue is a great one to tackle by newcomers to the project or OSS in general.
- **rfc** - Indicates that there is an RFC associated with this issue.
