# Recommended Practices

This document serves as reference for current practices and patterns that we want to standardize across Amundsen's frontend application code. Below, we provide some high-level guidelines targeted towards new contributors or any contributor who does not yet have domain knowledge in a particular framework or core library. This document is **not** intended to provide an exhaustive checklist for completing certain tasks.

We aim to maintain a reasonably consistent code base through these practices and welcome PRs to update and improve these recommendations.

## Code Styleguide

We have our coding styleguide baked into our [ESLint and Prettier rules](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/package.json#L261) for TypeScript code an [Stylelint rules](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/static/package.json#L556) for Sass code.

Looking forward, we aim at setting more strict best practices using ESLint and Stylelint. For that, we are leveraging a project called [betterer](https://github.com/phenomnomnominal/betterer), which keeps track of our errors when a given test is passed. You can run it using `npm run betterer` and it will break if you introduce any new eslint errors. If you want to ignore the new errors you can run `npm run betterer:update` to update the betterer.results file. We do not recommend adding or introducing new eslint errors.

## Naming Conventions
React is not opinionated about the naming of our components. Having freedom is great, but this sometimes comes at the cost of lack of consistency on the API.

To make sure Amundsen's React application is consistent and intuitive to use, we created this document that will describe the naming conventions for the React components.

### Component Names

#### View Components

We will follow this convention for naming our regular “view” components:

_[Context]ComponentName[Type]_

Where:
*   Context - the parent component or high-level page
*   ComponentName - what this component does. The responsibility of the component
*   Type - the type of component. Usually they are views, but they could be a Form, a List, a Figure, an Illustration, a Container

Examples:
*   SideBar (root component)
*   FooterSideBar (with context)
*   SideBarForm (with component type)
*   FooterSideBarForm (with all)


#### Custom Hook Components

We will name custom hook components with a name starting with “use”, as mentioned on the [official docs](https://reactjs.org/docs/hooks-custom.html#extracting-a-custom-hook).


#### High-order Components

We will name high order components (HOCs) using the “with” prefix. For example:

*   withAuthentication
*   withSubscription


#### Provider/Consumer Components

Whenever we need to use the Provider/Consumer pattern and name the components, we will use the “Provider” and “Consumer” suffixes. For example:

*   LoginProvider/LoginConsumer
*   DataProvider/DataConsumer


### Prop Names

#### Handler Functions

We will use the “on” prefix for handler functions, optionally adding a “subject” word before the event. The schema would be “on[Subject]Event”, for example:

*   onClick
*   onItemClick
*   onLogoHover
*   onFormSubmit

Internally, we will use the “handle” prefix for naming the handling functions, with an optional “subject” word in the middle. The schema would be then “handle[Subject]Event”, for example:

*   handleClick
*   handleButtonClick
*   handleHeadingHover

#### Props by Type

Props should be named to **describe** the component itself, and what it does, but not why it does it.

*   Objects - Use a singular noun
    *   item
*   Arrays - Use a plural noun
    *   items
    *   users
*   Numbers - Use a name with “num” prefix or with “count” or “index” suffix.
    *   numItems
    *   userCount
    *   itemIndex
*   Booleans - Use a “is”, “has”, or “can” prefix
    *   “is” for visual variations
        *   isVisible
        *   isEnabled
        *   isActive
    *   “is” also for behavioral or conditional variations
        *   isToggleable
        *   isExpandable
    *   “has” for toggling UI elements
        *   hasCancelSection
        *   hasHeader
*   React Nodes - use “element” suffix
    *   buttonElement
    *   itemElement

## Unit Testing

We use [Jest](https://jestjs.io/) as our test framework. We leverage utility methods from [Enzyme](https://airbnb.io/enzyme/) to test React components, and use [redux-saga-test-plan](https://github.com/jfairbank/redux-saga-test-plan#documentation) to test our `redux-saga` middleware logic.

### General

1. Leverage TypeScript to prevent bugs in unit tests and ensure that code is tested with inputs that match the defined interfaces and types. Adding and updating test [fixtures](https://github.com/amundsen-io/amundsen/tree/main/frontend/amundsen_application/static/js/fixtures) helps to provide re-useable pieces of typed test data or mock implementations for this purpose.
2. Leverage `beforeAll()`/`beforeEach()` for test setup when applicable. Leverage `afterAll()`/`afterEach` for test teardown when applicable to remove any side effects of the test block. For example if a mock implementation of a method was created in `beforeAll()`, the original implementation should be restored in `afterAll()`. See Jest's [setup-teardown documentation](https://jestjs.io/docs/en/setup-teardown) for further understanding.
3. Use descriptive title strings. To assist with debugging we should be able to understand what a test is checking for and under what conditions.
4. Become familiar with the variety of Jest [matchers](https://jestjs.io/docs/en/expect) that are available. Understanding the nuances of different matchers and the cases they are each ideal for assists with writing more robust tests. For example, there are many different ways to verify objects and the best matcher to use will depend on what exactly we are testing for. Examples:
   - If asserting that `inputObject` is assigned to variable `x`, asserting the equivalence of `x` using `.toBe()` creates a more robust test for this case because `.toBe()` will verify that the variable is actually referencing the given object. Contrast this to a matcher like `.toEqual()` which will verify whether or not the object happens to have a particular set of properties and values. In this case using `.toEqual()` would risk hiding bugs where `x` is not actually referencing `inputObject` as expected, yet happens to have the same key value pairs perhaps due to side effects in the code.
   - If asserting that `outputObject` matches `expectedObject`, asserting the equivalence of each property on `outputObject` using `.toBe()` or asserting the equality of the two objects using `.toMatchObject()` is useful when we only care that certain values exist on `outputObject`. However if it matters that certain values **do not** exist on `outputObject` -- as is the case with reducer outputs -- `.toEqual()` is a more robust alternative as it compares all properties on both objects for equivalence.
5. When testing logic that makes use of JavaScript's _Date_ object, note that our Jest scripts are configured to run in the UTC timezone. Developers should either:
   - Mock the _Date_ object and its methods' return values, and run assertions based on the mock values.
   - Create assertions knowing that the unit test suite will run as if we are in the UTC timezone.
6. Code coverage is important to track but it only informs us of what code was actually run and executed during the test. The onus is on the developer to focus on use case coverage and make sure that right assertions are run so that all logic is adequately tested.

### React

1. Enzyme provides 3 different utilities for rendering React components for testing. We recommend using `mount` rendering so you can dive deep on the rendered output.
2. Create a re-useable `setup()` function that will take any arguments needed to test conditional logic.
3. Look for opportunities to organize tests a way such that one `setup()` can be used to test assertions that occur under the same conditions. For example, a test block for a method that has no conditional logic should only have one `setup()`. However, it is **not** recommended to share a `setup()` result across tests for different methods, or across tests for a method that has a dependency on a mutable piece of state. The reason is that we risk propagating side effects from one test block to another.
4. Consider refactoring components or other files if they become burdensome to test. Potential options include (but are not limited to):
   - Create subcomponents for large components. This is also especially useful for reducing the burden of updating tests when component layouts are changed.
   - Break down large functions into smaller functions. Unit test the logic of the smaller functions individually, and mock their results when testing the larger function.
   - Export constants from a separate file for hardcoded values and import them into the relevant source files and test files. This is especially helpful for strings.

### Redux

1. Because the majority of Redux code consists of functions, we unit test those methods as usual and ensure the functions produce the expected output for any given input. See Redux's documentation on testing [action creators](https://redux.js.org/recipes/writing-tests#action-creators), [async action creators](https://redux.js.org/recipes/writing-tests#async-action-creators), and [reducers](https://redux.js.org/recipes/writing-tests#reducers), or check out examples in our code.
2. Unless an action creator includes any logic other than returning the action, unit testing the reducer and saga middleware logic is sufficient and provides the most value.
3. `redux-saga` generator functions can be tested by iterating through it step-by-step and running assertions at each step, or by executing the entire saga and running assertions on the side effects. See redux-saga's documentation on [testing sagas](https://redux-saga.js.org/docs/advanced/Testing.html) for a wider breadth of examples.


## Reference
*   [How to name props for React components – David's Blog](https://dlinau.wordpress.com/2016/02/22/how-to-name-props-for-react-components/)
*   [Handy Naming Conventions for Event Handler Functions & Props in React | by Juan Bernal | JavaScript In Plain English | Medium](https://medium.com/javascript-in-plain-english/handy-naming-conventions-for-event-handler-functions-props-in-react-fc1cbb791364)
*   [https://medium.com/@wittydeveloper/react-components-naming-convention-%EF%B8%8F-b50303551505](https://medium.com/@wittydeveloper/react-components-naming-convention-%EF%B8%8F-b50303551505)
*   [https://reactjs.org/docs/hooks-custom.html#extracting-a-custom-hook](https://reactjs.org/docs/hooks-custom.html#extracting-a-custom-hook)
*   [https://reactjs.org/docs/higher-order-components.html](https://reactjs.org/docs/higher-order-components.html)
