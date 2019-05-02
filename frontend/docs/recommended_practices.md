# Recommended Practices

This document serves as reference for current practices and patterns that we want to standardize across Amundsen's frontend application code. Below, we provide high-level guidelines targeted towards new contributors or any contributor who does not yet have domain knowledge in a particular framework or core library. This document is **not** intended to provide an exhaustive checklist for completing certain tasks.

We aim to maintain a reasonably consistent code base through these practices and welcome PRs to update and improve these recommendations.

## React Application
### Unit Testing
We use [Jest](https://jestjs.io/) as our test framework and leverage utility methods from [Enzyme](https://airbnb.io/enzyme/) to test React components.

#### Recommendations
1. Leverage TypeScript to prevent bugs in unit tests and ensure that components are tested with data that matches their defined interfaces. Adding and updating test [fixtures](https://github.com/lyft/amundsenfrontendlibrary/tree/master/amundsen_application/static/js/fixtures) helps to provide re-useable pieces of typed test data for our code.
2. Enzyme provides 3 different utilities for rendering React components for testing. We recommend using `shallow` rendering to start off. If a component has a use case that requires full DOM rendering, those cases will become apparent. See Enzyme's [api documentation](https://airbnb.io/enzyme/docs/api/) to read more about the recommendations for each option.
3. Create a re-useable `setup()` function that will take any arguments needed to test conditional logic.
4. Look for opportunities to organize tests a way such that one `setup()` can be used to test assertions that occur under the same conditions. For example, a test block for a method that has no conditional logic should only have one `setup()`. However, it is **not** recommended to share a `setup()` result across tests for different methods because we risk propagating side effects from one test block to another.
5. Leverage `beforeAll()`/`beforeEach()` for test setup when applicable. Leverage `afterAll()`/`afterEach` for test teardown to remove any side effects of the test block. For example if a mock implementation of a method was created in `beforeAll()`, the original implementation should be restored in `afterAll()`. See Jest's [setup-teardown documentation](https://jestjs.io/docs/en/setup-teardown) for further understanding.
6. Use descriptive title strings. To assist with debugging we should be able to understand what a test is checking for, and under what conditions.
7. Consider refactoring components or other files if they become burdensome to test. Potential options include (but are not limited to):
   * Creating subcomponents for large components, or breaking down large functions.
   * Export constants from a separate file for hardcoded values and import them into the relevant source files and test files. This is especially helpful for strings.
8. Code coverage is important to track but it only informs us of what code was actually run and executed during the test. The onus is on the developer to make sure that right assertions are run and that logic is adequately tested.
