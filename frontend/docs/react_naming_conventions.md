# Amundsen's React Naming Conventions
> A guide for naming React components on Amundsen

React is not opinionated about the naming of our components. Having freedom is great, but this sometimes comes at the cost of lack of consistency on the API.

To make sure Amundsen's React application is consistent and intuitive to use, we created this document that will describe the naming conventions for the React components.

## Component Names

### View Components

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


### Custom Hook Components

We will name custom hook components with a name starting with “use”, as mentioned on the [official docs](https://reactjs.org/docs/hooks-custom.html#extracting-a-custom-hook).


### High-order Components

We will name high order components (HOCs) using the “with” prefix. For example:

*   withAuthentication
*   withSubscription


### Provider/Consumer Components

Whenever we need to use the Provider/Consumer pattern and name the components, we will use the “Provider” and “Consumer” suffixes. For example:

*   LoginProvider/LoginConsumer
*   DataProvider/DataConsumer


## Prop Names

### Handler Functions

We will use the “on” prefix for handler functions, optionally adding a “subject” word before the event. The schema would be “on[Subject]Event”, for example:

*   onClick
*   onItemClick
*   onLogoHover
*   onFormSubmit

Internally, we will use the “handle” prefix for naming the handling functions, with an optional “subject” word in the middle. The schema would be then “handle[Subject]Event”, for example:

*   handleClick
*   handleButtonClick
*   handleHeadingHover

### Props by Type

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


## Reference
*   [How to name props for React components – David's Blog](https://dlinau.wordpress.com/2016/02/22/how-to-name-props-for-react-components/)
*   [Handy Naming Conventions for Event Handler Functions & Props in React | by Juan Bernal | JavaScript In Plain English | Medium](https://medium.com/javascript-in-plain-english/handy-naming-conventions-for-event-handler-functions-props-in-react-fc1cbb791364)
*   [https://medium.com/@wittydeveloper/react-components-naming-convention-%EF%B8%8F-b50303551505](https://medium.com/@wittydeveloper/react-components-naming-convention-%EF%B8%8F-b50303551505)
*   [https://reactjs.org/docs/hooks-custom.html#extracting-a-custom-hook](https://reactjs.org/docs/hooks-custom.html#extracting-a-custom-hook) 
*   [https://reactjs.org/docs/higher-order-components.html](https://reactjs.org/docs/higher-order-components.html) 
