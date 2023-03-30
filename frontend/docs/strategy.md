# **Amundsen Frontend Strategy**
> A vision and strategy for Amundsen’s Frontend

##  1. <a name='overview'></a>Overview

Amundsen’s UI hasn’t had a lot of updates on our front-end application in the last year. As a side effect, the code is suffering from stagnation. The team had to hold off on solving some of the user experience and quality issues due to limited resourcing. This is a problem because this can **slow velocity** and critical updates become more urgent if we don’t focus our limited resources in the right direction.

One thing we can do is to create a **technical strategy** that sets a direction for contributors and maintainers on the front-end that allows them to align, make quick, confident decisions and improve the effectiveness of the resources we have.

>Table of Contents
<!-- vscode-markdown-toc -->
* 1. [Overview](#overview)
* 2. [What](#what)
* 3. [Where are we today](#where-are-we-today)
  * 3.1. [User Experience](#user-experience)
  * 3.2. [Codebase Quality](#codebase-quality)
  * 3.3. [Developer Experience and Collaboration](#developer-experience-and-collaboration)
* 4. [Where we want to be](#where-we-want-to-be)
  * 4.1. [User Experience](#user-experience-1)
  * 4.2. [Codebase Quality](#codebase-quality-1)
  * 4.3. [Developer Experience and Collaboration](#developer-experience-and-collaboration-1)
* 5. [Current State and Vision Summary](#current-state-and-vision-summary)
* 6. [Next Steps](#next-steps)
  * 6.1. [Prioritized Milestones](#prioritized-milestones)
    * 6.1.1. [Milestone 1: Increase OSS contributions and remove critical team devex issues](#milestone-1:-increase-oss-contributions-and-remove-critical-team-devex-issues)
    * 6.1.2. [Milestone 2: Eliminate main User reported issues](#milestone-2:-eliminate-main-user-reported-issues)
    * 6.1.3. [Milestone 3: Reduce dependencies issues and improve testing](#milestone-3:-reduce-dependencies-issues-and-improve-testing)
* 7. [Appendix A: Prioritization Process](#appendix-a:-prioritization-process)
  * 7.1. [User Experience](#user-experience-2)
  * 7.2. [Codebase Quality](#codebase-quality-2)
  * 7.3. [Developer Experience and Collaboration](#developer-experience-and-collaboration-2)
  * 7.4. [Next steps (by cost/impact)](#next-steps-(by-cost/impact))
  * 7.5. [Prioritized Improvements](#prioritized-improvements)
* 8. [Appendix B: Why we got here](#appendix-b:-why-we-got-here)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->


##  2. <a name='what'></a>What
A technical strategy is a **tool of proactive alignment that empowers teams to move quickly and with confidence.** A great technical strategy identifies a problem with the current situation, proposes a principled approach to overcome it, and then shows you a coherent roadmap to follow.

This Strategy will break down into three parts:
* Where are we now (Current State)
* Where do we want to get to (Target State)
* What are we doing next (Next Steps)

##  3. <a name='where-are-we-today'></a>Where are we today
To create a strategy for Amundsen’s UI in the near future, we need to know where we are today. Here we’ll describe it with the following considerations:
* **User Experience** - How our final users experience the UI and how well they can perform their tasks.
* **Codebase Quality** - The quality of the codebase, how fast we can extend it with new features without hurting stability.
* **Developer Experience & Collaboration** - How easy is for new contributors to start helping in the project.

###  3.1. <a name='user-experience'></a>User Experience
We **lack consistency and a polished user experience**. We can summarize it on these points:
* Inconsistent typography
* Inconsistent buttons and links
* Not a11y WAG 2.1 compliant
* Inconsistent error handling
* Limited “browsing” experience
* Bulky components & layout
* Homepage page is not tailored to user role
* Cluttered metadata on the left panel of the Table Detail page
* Differing list components across different pages and even within the same page across different tabs

###  3.2. <a name='codebase-quality'></a>Codebase Quality
There are some aspects where the current codebase is sub-par:
* Many old ESLint issues still around, like:
    * Not destructing props
    * Usage of setState within componentDidUpdate
* Human-readable strings hardcoded on JSX code
* Sub-optimal state management
    * Scattered and inconsistent Redux logic for extracting info
    * Complex and boilerplate full Redux logic
* Incomplete testing
    * Outdated unit testing library (Enzyme, 107 files)
    * Incomplete unit test coverage
    * No end to end testing
* Scattered URL logic
* Sub-par API
    * No API type Verification
    * Non-cleaned deprecated endpoints
    * Inconsistent functionality between endpoints for different resources
* Many bugs in the codebase
* No code health monitoring
* Deprecated component library
* Outdated React Version (v16)

###  3.3. <a name='developer-experience-and-collaboration'></a>Developer Experience and Collaboration
Developers bump into friction when dealing with the following issues:
* Scattered fixture data for our unit tests
* Hard to figure out typography
* Inconsistent and incomplete instrumentation
* No test coverage tracking
* Incomplete Documentation
    * Incomplete frontend configuration documentation
    * No code style guide
    * No naming conventions
* Outdated Docker image for getting started with Amundsen for OSS
    * Missing showcase of configurable features
    * Outdated versions of all packages
* No PR Previews
* Complex and brittle developer environment setup
* Custom React application on top of Flask


##  4. <a name='where-we-want-to-be'></a>Where we want to be
Now that we have established where we are today (as of Jan 2023); let’s now describe where we want to be within a medium to long term. We will repeat the previous grouping:

###  4.1. <a name='user-experience-1'></a>User Experience
* Consistent typography
* Consistent buttons and links
* A11y WAG 2.1 compliant
* Consistent and efficient error handling
* Delightful “browsing” experience
* Information-dense components & layout
* Tailored and configurable homepage
* Tidy Table Detail page metadata
* Consistent list components


###  4.2. <a name='codebase-quality-1'></a>Codebase Quality
* No ESLint warnings
* All human-readable strings as constants
* Optimal state management
    * Testable and extensible Redux logic for extracting info
    * More maintainable Redux logic
* Thorough testing
    * Using React Testing Library
    * Fully tested codebase (80%+)
    * With end to end testing
* Centralized URL logic
* Pristine API
    * Tested API type verification
    * Non-deprecated endpoints
    * Consistent functionality between endpoints for different resources
* Bug-free code
* With codebase health monitoring
* Up to date component library
* Up to date React (v18)


###  4.3. <a name='developer-experience-and-collaboration-1'></a>Developer Experience and Collaboration
* Extendable fixture data we can use to manually test the UI
* Limited typography options
* Thorough and extensible instrumentation
* Easily tracked test coverage that breaks builds when reduced
* Thorough Documentation
    * Thorough frontend configuration documentation with examples
    * Complete code style guide
    * Naming conventions
* Up to date Docker image for OSS
    * Including showcase of configurable features
    * Updated versions of all packages
* Previews with PRs
* Easy developer environment setup
* React framework (Next.js) independent from flask API


##  5. <a name='current-state-and-vision-summary'></a>Current State and Vision Summary
<table>
  <tr>
   <td><strong>Consideration</strong>
   </td>
   <td><strong>Current State</strong>
   </td>
   <td><strong>Target State</strong>
   </td>
  </tr>
  <tr>
   <td rowspan="9" ><strong>User Experience</strong>
   </td>
   <td>Inconsistent typography
   </td>
   <td>Consistent typography
   </td>
  </tr>
  <tr>
   <td>Inconsistent buttons and links
   </td>
   <td>Consistent buttons and links
   </td>
  </tr>
  <tr>
   <td>Not a11y WAG 2.1 compliant
   </td>
   <td>A11y WAG 2.1 compliant
   </td>
  </tr>
  <tr>
   <td>Inconsistent error handling
   </td>
   <td>Consistent and efficient error handling
   </td>
  </tr>
  <tr>
   <td>Limited “browsing” experience
   </td>
   <td>Delightful “browsing” experience
   </td>
  </tr>
  <tr>
   <td>Bulky components & layout
   </td>
   <td>Information-dense components & layout
   </td>
  </tr>
  <tr>
   <td>Homepage page is not tailored to user role
   </td>
   <td>Tailored and configurable homepage
   </td>
  </tr>
  <tr>
   <td>Cluttered metadata on the left panel of the Table Detail page
   </td>
   <td>Tidy Table Detail page metadata
   </td>
  </tr>
  <tr>
   <td>Differing list components across pages or tabs
   </td>
   <td>Consistent list components
   </td>
  </tr>
  <tr>
   <td rowspan="10" ><strong>Codebase Quality</strong>
   </td>
   <td>Many old ESLint issues still around, like:
<ul>

<li>Not destructing props

<li>Usage of setState within componentDidUpdate
</li>
</ul>
   </td>
   <td>No ESLint warnings
   </td>
  </tr>
  <tr>
   <td>Human-readable strings hardcoded on JSX code
   </td>
   <td>All human-readable strings as constants
   </td>
  </tr>
  <tr>
   <td>Sub-optimal state management
<ul>

<li>Scattered and inconsistent Redux logic for extracting info

<li>Complex and boilerplate full Redux logic
</li>
</ul>
   </td>
   <td>Optimal state management
<ul>

<li>Testable and extensible Redux logic for extracting info

<li>More maintainable Redux logic
</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>Incomplete testing
<ul>

<li>Outdated unit testing library (Enzyme)

<li>Incomplete unit test coverage

<li>No end to end testing
</li>
</ul>
   </td>
   <td>Thorough testing
<ul>

<li>Using React Testing Library

<li>Fully tested codebase (80%+)

<li>With end to end testing
</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>Scattered URL logic
   </td>
   <td>Centralized URL logic
   </td>
  </tr>
  <tr>
   <td>Sub-par API
<ul>

<li>No API type Verification

<li>Non-cleaned deprecated endpoints

<li>Inconsistent functionality between endpoints for different resources
</li>
</ul>
   </td>
   <td>Pristine API
<ul>

<li>Tested API type verification

<li>Non-deprecated endpoints

<li>Consistent functionality between endpoints for different resources
</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>Many bugs in the codebase
   </td>
   <td>Bug-free code
   </td>
  </tr>
  <tr>
   <td>No code health monitoring
   </td>
   <td>With codebase health monitoring
   </td>
  </tr>
  <tr>
   <td>Deprecated component library
   </td>
   <td>Up to date component library
   </td>
  </tr>
  <tr>
   <td>Outdated React Version (v16)
   </td>
   <td>Up to date React (v18)
   </td>
  </tr>
  <tr>
   <td rowspan="9" ><strong>Developer Experience and Collaboration</strong>
   </td>
   <td>Scattered fixture data for our unit tests
   </td>
   <td>Extendable fixture data we can use to manually test the UI
   </td>
  </tr>
  <tr>
   <td>Hard to figure out typography
   </td>
   <td>Limited typography options
   </td>
  </tr>
  <tr>
   <td>Inconsistent and incomplete instrumentation
   </td>
   <td>Thorough and extensible instrumentation
   </td>
  </tr>
  <tr>
   <td>No test coverage tracking
   </td>
   <td>Easily tracked test coverage that breaks builds when reduced
   </td>
  </tr>
  <tr>
   <td>Incomplete Documentation
<ul>

<li>Incomplete frontend configuration documentation

<li>No code style guide

<li>No naming conventions
</li>
</ul>
   </td>
   <td>Thorough Documentation
<ul>

<li>Thorough frontend configuration documentation with examples

<li>Complete code style guide

<li>Naming conventions
</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>Outdated Docker image for getting started with Amundsen for OSS
<ul>

<li>Missing showcase of configurable features

<li>Outdated versions of all packages
</li>
</ul>
   </td>
   <td>Up to date Docker image for OSS
<ul>

<li>Including showcase of configurable features

<li>Updated versions of all packages
</li>
</ul>
   </td>
  </tr>
  <tr>
   <td>No PR Previews
   </td>
   <td>Previews with PRs
   </td>
  </tr>
  <tr>
   <td>Complex and brittle developer environment setup
   </td>
   <td>Easy developer environment setup
   </td>
  </tr>
  <tr>
   <td>Custom React application on top of Flask
   </td>
   <td>React framework (Next.js) independent from flask API
   </td>
  </tr>
</table>

##  6. <a name='next-steps'></a>Next Steps

We have seen where we think we are right now, and where we want to be in the future. The changes are many, so what are our next steps? In this section, we describe the changes we’ll need to introduce to take us to our vision.

###  6.1. <a name='prioritized-milestones'></a>Prioritized Milestones

From the next steps task prioritization (see Appendix B), we have grouped tasks into Milestones that will target specific metrics. Here is our proposal:

####  6.1.1. <a name='milestone-1:-increase-oss-contributions-and-remove-critical-team-devex-issues'></a>Milestone 1: Increase OSS contributions and remove critical team devex issues
**Metrics**:
* _Increased number of contributions (in PR numbers)_
* _Team time savings (estimation)_

**Success Condition**: We increase the monthly contributions by 20%

**Tasks**:
1. Update Docker image for OSS - Adding a showcase of configurable features
2. Fix developer environment setup - Create a document of the current setup that works 100% of the times using Lyft’s tooling and Python version
3. Improve error handling - Provide useful Metadata, and API error messages
4. Add end to end testing - running them on the development machine and covering the main user flows
5. Improve Documentation - Improve our frontend configuration documentation
    1. Complete docs with all the rest of config options
    2. Add examples to all the options
    3. Structure docs
6. Get PR previews working and usable - with extensive test data
7. Improve test coverage - 100% test coverage on config-utils and util files
8. Improve Documentation - Create a code style guide and naming conventions

####  6.1.2. <a name='milestone-2:-eliminate-main-user-reported-issues'></a>Milestone 2: Eliminate main User reported issues

**Metrics**: Customer satisfaction (Surveyed)

**Success Condition**: We increase customer satisfaction by 20% (NPS score or other metric)

**Tasks**:
1. Improve error handling - Provide useful or actionable UI error messages
2. Organize the left sidebar of the Table Detail Page - Move information into expandable blocks
3. Organize the left sidebar of the Table Detail Page - Declutter features
4. Squash all outstanding bugs
5. Improve error handling - Improve user experience when token expires

####  6.1.3. <a name='milestone-3:-reduce-dependencies-issues-and-improve-testing'></a>Milestone 3: Reduce dependencies issues and improve testing

**Metrics**: Team time savings (estimation)

**Success Condition**: We have no issues when bumping OSS project versions

**Tasks**:
1. Update Docker image for OSS - Update versions of all packages
2. Fix our developer environment setup - Simplify setup if possible
    1. Align internal and external python package versions as much as possible for easier installation and pyenv setup
3. Add end to end testing - Running on CI and covering secondary user flows
4. Improve test coverage - 90% test coverage on presentational components and 80% overall test coverage



##  7. <a name='appendix-a:-prioritization-process'></a>Appendix A: Prioritization Process
After we synced on where we think we are right now, and where we want to be in the future, we got many tasks. So what are our next steps? In this section, we describe the changes we’ll need to introduce to take us to our vision.

We will add an extra category to the improvements: their **benefits to our users, and to the OSS team**. For that, we will include these _labels_:

1. **&lt;UT>** - Improvements that save time to our users
2. **&lt;DEXP>** - Improvements that save time to our team
    * By reducing the maintenance burden
    * By reducing the time to create features and debug issues
    * By reducing friction for new OSS contributions, effectively getting more help

Let’s see the improvements with the initial categories and their benefits:

###  7.1. <a name='user-experience-2'></a>User Experience
* Improve our typography - &lt;DEXP>
    * Remove old classes
* Improve our buttons - &lt;DEXP>
    * Audit our buttons in Storybook
    * Audit our links in Storybook
    * Update all our buttons and links to be consistent
    * Add missing styles
* Improve our a11y - &lt;UT>
    * Audit a11y
    * Fix a11y issues
    * Setup automated testing to catch regressions
* Improve error handling - &lt;DEXP>, &lt;UT>
    * Handle errors at the right level and with useful feedback
    * Improve experience when token expires
* Improve our browsing experience - &lt;UT>
    * Complete our transition to faceted search on the search page
    * Add a basic browse experience to complement the faceted search
* Bulky components & layout - &lt;UT>
    * Update our components to be more compact
    * Update our layout to be more compact
    * Update table detail page left panel to look more orderly when a table has many of the ‘optional’ fields displayed.
* Homepage page is not tailored to user role - &lt;UT>
    * Move our announcements section into a drawer that opens from the global header
    * Improve our homepage layout to contain more customizable widgets
* Organize the left sidebar of the Table Detail Page - &lt;UT>
    * Move information into blocks
    * Reorganize the blocks and open those more important for our users
* Make the lists/tables consistent - &lt;DEXP>
    * Decide for one way of listing elements
    * Roll it out all over the UI


###  7.2. <a name='codebase-quality-2'></a>Codebase Quality
* Fix all the ESLint warnings - &lt;DEXP>
    * Destructuring
    * SetState issues
* Improve State Management - &lt;DEXP>
    * Create Redux selectors whenever we can
    * Explore using Redux toolkit to simplify our Redux logic
* Improve Testing - &lt;DEXP>
    * Migrate Enzyme tests into React Testing Library &lt;DEXP>
        * Audit work
        * Create tickets and find support
        * Migrate tests
    * Improve test coverage - &lt;DEXP>
        * 100% test coverage on config-utils
        * 100% test coverage on util files
        * 90% test coverage on presentational components
        * 80% overall test coverage components
    * Add end to end testing - &lt;UT>, &lt;DEXP>
        * Cover main user flows
        * Cover secondary user flows
        * Ran on CI
* Centralize URL logic - &lt;DEXP>
    * Create util file with static URLs
    * Extend with dynamic URLs
* Improve our API - &lt;DEXP>
    * Runtime type checking with [https://gcanti.github.io/io-ts/](https://gcanti.github.io/io-ts/)
    * Clean up all deprecated endpoints
    * Refactor resource endpoints to make them consistent
* Squash all the bugs - &lt;UT>
    * Critical
    * Major
    * Minor
* Add codebase health monitoring - &lt;DEXP>
    * Find a free solution for OSS (code climate?)
    * Introduce it
    * Break builds with degradations
* Update component library - &lt;DEXP>
* Update React version - &lt;DEXP>
    * Depends on moving to React Testing Library
    * Update codebase using codemods


###  7.3. <a name='developer-experience-and-collaboration-2'></a>Developer Experience and Collaboration
* Fix our fixture data - &lt;DEXP>
    * Create test data builders for all our fixtures
    * Create a debug mode to use the test data for manual testing of features
* Easy to use text component - &lt;DEXP>
* Improved instrumentation - &lt;DEXP>
    * Actions with analytics payloads
    * Make sure all feature utilization is accurately tracked 4
* Test coverage tracking - &lt;DEXP>
    * Use codecov to track test coverage
    * Use codecov to break builds when reducing by a given %
* Improve Documentation - &lt;DEXP>
    * Improve our frontend configuration documentation
        * Complete docs with all the rest of config options
        * Add examples to all the options
        * Structure docs
    * Create a code styleguide
    * Create naming conventions
* Update Docker image for OSS - &lt;DEXP>
    * Add showcase of configurable features
    * Update versions of all packages
* Get Uffici tool merged and usable - &lt;DEXP>
* Fix our developer environment setup - &lt;DEXP>
    * Create a document of the current setup that works 100% of the times using Lyft’s tooling and Python version
    * Simplify setup if possible
* Migrate into using Next.js - &lt;DEXP>
    * Pick between the many approaches to [incrementally adopt Next.js](https://nextjs.org/docs/migrating/incremental-adoption)
    * Move out the application part by part into Next.js keeping Flask as the API server


###  7.4. <a name='next-steps-(by-cost/impact)'></a>Next steps (by cost/impact)
We have seen the gap we’ll need to cover in each consideration group and our vision for them. Now, we’ll look at the work from an **impact** point of view. We will prioritize things with the highest leverage and tasks we should do first to make others easier later.

For that, we have estimated the **impact** (from 0 to 5) and **cost** (T-Shirt sizing), and prioritized the improvements in the following list:

###  7.5. <a name='prioritized-improvements'></a>Prioritized Improvements
1. Update Docker image for OSS - &lt;DEXP> | Impact - 4 5 5 5 - **5** | Cost - **S**
    1. Add showcase of configurable features
    2. Update versions of all packages

2. Fix our developer environment setup - &lt;DEXP> | Impact - 4 5 5 4 - **4.5 **| Cost** - M**
    1. Create a document of the current setup that works 100% of the times using Lyft’s tooling and Python version
    1. Simplify setup if possible
        1. Align internal and external python package versions as much as possible for easier installation and pyenv setup

3. Improve error handling - &lt;DEXP>, &lt;UT> | Impact - 4 4 4 3 4 - **4 **| Cost **- M**
    1. Provide useful Metadata error messages
    1. Provide useful API error messages
    1. Provide useful UI messaging
    1. Improve experience when token expires

4. Organize the left sidebar of the Table Detail Page - &lt;UT> | Impact - 5 3 5 4 4 - **4 **| Cost -** M**
    1. Move information into blocks
    1. Reorganize the blocks and open those more important for our users
    1. Later: declutter

5. Add end to end testing - &lt;UT>, &lt;DEXP> | Impact - 4 5 4 - **4.5 **| Cost **- L**
    1. Depends on Docker image working
    1. Ran in Dev machine
    1. Cover main user flows
    1. Cover secondary user flows
    1. Ran on CI

6. Squash all the bugs - &lt;UT> | Impact - 4 4 3 5 4 - **4 **| Cost **- S**
    1. Critical
    1. Major
    1. Minor

7. Improve Documentation - &lt;DEXP> | Impact - 5 4 4 3 4 - **4 **| Cost -** M**
    1. Improve our frontend configuration documentation
        2. Complete docs with all the rest of config options
        3. Add examples to all the options
        4. Structure docs
    1. Create a code styleguide
    1. Create naming conventions

8. Get Uffici tool merged and usable - &lt;DEXP> | Impact - 4 3 3 4 - **3.5 **| Cost -** M**
    1. Depends on the docker task

9. Improve test coverage - &lt;DEXP> | Impact - 4 3 - **3.5 **| Cost **- M**
    1. 100% test coverage on config-utils
    1. 100% test coverage on util files
    1. 90% test coverage on presentational components
    1. 80% overall test coverage components

10. Migrate Enzyme tests into React Testing Library &lt;DEXP> | Impact - 3 3 - **3** | Cost -
    1. Audit work
    1. Create tickets and find support
    1. Migrate tests

11. Migrate into using Next.js - &lt;DEXP> | Impact - 3 2 3 4 - **3** | Cost -
    1. Pick between the many approaches to [incrementally adopt Next.js](https://nextjs.org/docs/migrating/incremental-adoption)
    1. Move out the application part by part into Next.js keeping Flask as the API server

12. Improve our browsing experience - &lt;UT> | Impact - 3 2 3 2 3 - **3** | Cost -
    1. Complete our transition to faceted search on the search page
    1. Add a basic browse experience to complement the faceted search

13. Bulky components & layout - &lt;DP> | Impact - 4 2 3 3 3 - **3** | Cost -
    1. Update our components to be more compact
    1. Update our layout to be more compact
    1. Update table detail page left panel to look more orderly when a table has many of the ‘optional’ fields displayed.

14. Homepage page is not tailored to user role - &lt;UT> | Impact - 4 3  4 2 3 - **3** | Cost -
    1. Move our announcements section into a drawer that opens from the global header
    1. Improve our homepage layout to contain more customizable widgets

15. Improve State Management - &lt;DEXP> | Impact - 1 3 3 3 - **3** | Cost -
    1. Create Redux selectors whenever we can
    1. Explore using Redux toolkit to simplify our Redux logic

16. Improve our API - &lt;DEXP> | Impact - 4 3 3 3 - **3** | Cost -
    1. Runtime type checking with [https://gcanti.github.io/io-ts/](https://gcanti.github.io/io-ts/)
    1. Clean up all deprecated endpoints
    1. Refactor resource endpoints to make them consistent

17. Add codebase health monitoring - &lt;DEXP> | Impact - 2 3 4 3 - **3** | Cost -
    1. Find a free solution for OSS (code climate?)
    1. Introduce it
    1. Break builds with degradations

18. Update component library - &lt;DEXP> | Impact - 2 3 3 3 4 - **3** | Cost -

19. Improved instrumentation - &lt;DEXP> | Impact - 1 3 2 3 - **3** | Cost -
    1. Actions with analytics payloads
    1. Make sure all feature utilization is accurately tracked

20. Test coverage tracking - &lt;DEXP> | Impact - 2 3 3 2 - **2.5** | Cost -
    1. Use codecov to track test coverage
    1. Use codecov to break builds when reducing by a given %

21. Improve our typography - &lt;DEXP> | Impact - 1 2 2 1 2 - **2 **| Cost -
    1. Remove old classes

22. Improve our buttons - &lt;DEXP> | Impact - 2 2 2 1 2 - **2 **| Cost -
    1. Audit our buttons in Storybook
    1. Audit our links in Storybook
    1. Update all our buttons and links to be consistent
    1. Add missing styles

23. Improve our a11y - &lt;UT> | Impact - 2 3 1 1 1 - **2 **| Cost -
    1. Audit a11y
    1. Fix a11y issues
    1. Setup automated testing to catch regressions

24. Make the lists/tables consistent - &lt;DEXP>, &lt;DP> | Impact - 2 1 3 2 2 - **2** | Cost -
    1. Decide for one way of listing elements
    1. Roll it out all over the UI

25. Fix all the ESLint warnings - &lt;DEXP> | Impact - 2 2 2 2 -** 2** | Cost -
    1. Destructuring
    1. SetState issues

26. Centralize URL logic - &lt;DEXP> | Impact - 2 2 2 2 - **2** | Cost -
    1. Create util file with static URLs
    1. Extend with dynamic URLs

27. Update React version - &lt;DEXP> | Impact - 1 2 2 3 - **2** | Cost -
    1. Depends on moving to React Testing Library
    1. Update codebase using codemods

28. Fix our fixture data - &lt;DEXP> | Impact - 2 2 2 3 - **2** | Cost -
    1. Create test data builders for all our fixtures
    1. Create a debug mode to use the test data for manual testing of features

29. Easy to use text component - &lt;DEXP> | Impact - 1 1 3 1 3 - **2** | Cost -


##  8. <a name='appendix-b:-why-we-got-here'></a>Appendix B: Why we got here

There is no single reason for the current state of our frontend codebase, however, we can relate to the following reasons (among others):
* Lack of resources
* Lack of OSS contributions to the UI
* General Stagnation of the community
