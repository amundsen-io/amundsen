import * as React from 'react';

import { mount, shallow } from 'enzyme';

import { mapStateToProps, mapDispatchToProps, SearchBar, SearchBarProps } from '../';
import {
  ERROR_CLASSNAME,
  SUBTEXT_DEFAULT,
  SYNTAX_ERROR_CATEGORY,
  SYNTAX_ERROR_PREFIX,
  SYNTAX_ERROR_SPACING_SUFFIX,
} from '../constants';
import globalState from 'fixtures/globalState';
import { getMockRouterProps } from 'fixtures/mockRouter';

import { ResourceType } from 'interfaces';

document.addEventListener = jest.fn(() => {});
document.removeEventListener = jest.fn(() => {});

describe('SearchBar', () => {
  const valueChangeMockEvent = { target: { value: 'Data Resources' } };
  const submitMockEvent = { preventDefault: jest.fn() };
  const setStateSpy = jest.spyOn(SearchBar.prototype, 'setState');
  const setup = (propOverrides?: Partial<SearchBarProps>, useMount?: boolean) => {
    const props: SearchBarProps = {
      onInputChange: jest.fn(),
      onSelectInlineResult: jest.fn(),
      searchTerm: '',
      submitSearch: jest.fn(),
      ...propOverrides
    };
    const wrapper = useMount ? mount<SearchBar>(<SearchBar {...props} />) : shallow<SearchBar>(<SearchBar {...props} />);
    return { props, wrapper };
  };

  describe('constructor', () => {
    const searchTerm = 'data';
    const subText = 'I am some text';
    let wrapper;
    beforeAll(() => {
      wrapper = setup({ searchTerm, subText }).wrapper;
    });
    it('sets the searchTerm state from props', () => {
      expect(wrapper.state().searchTerm).toEqual(searchTerm);
    });

    it('sets the subText state from props', () => {
      expect(wrapper.state().subText).toEqual(subText);
    });
  });

  describe('clearSearchTerm', () => {
    it('sets the searchTerm to an empty string', () => {
      setStateSpy.mockClear();
      const initialSearchTerm = 'non empty search term';
      const { wrapper } = setup({ searchTerm: initialSearchTerm});
      expect(wrapper.state().searchTerm).toBe(initialSearchTerm);
      wrapper.instance().clearSearchTerm();
      expect(setStateSpy).toHaveBeenCalledWith({ searchTerm: '', showTypeAhead: false });
    });
  });

  describe('componentDidMount', () => {
    it('adds an event listener for updateTypeAhead to be called on mousedown', () => {
      const { wrapper } = setup({}, true);
      expect(document.addEventListener).toHaveBeenCalledWith('mousedown', wrapper.instance().updateTypeAhead, false);
    });
  });

  describe('componentWillUnmount', () => {
    it('removes the event listener for updateTypeAhead', () => {
      const { wrapper } = setup({}, true);
      wrapper.instance().componentWillUnmount();
      expect(document.removeEventListener).toHaveBeenCalledWith('mousedown', wrapper.instance().updateTypeAhead, false);
    });
  });

  describe('componentDidUpdate', () => {
    it('sets the searchTerm state when props update', () => {
      const { props, wrapper } = setup();
      const prevState = wrapper.state();
      props.searchTerm = 'newTerm';
      // @ts-ignore: Why does this work in other tests but complain here
      wrapper.setProps(props);
      expect(wrapper.state()).toMatchObject({
        ...prevState,
        searchTerm: 'newTerm',
      });
    });
  });

  describe('handleValueChange', () => {
    let shouldShowTypeAheadSpy;

    it('calls setState on searchTerm and shouldShowTypeAhead ', () => {
      const { props, wrapper } = setup();
      const mockReturnValue = true;
      shouldShowTypeAheadSpy = jest.spyOn(wrapper.instance(), 'shouldShowTypeAhead').mockImplementation(() => mockReturnValue);
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueChange(valueChangeMockEvent);
      expect(setStateSpy).toHaveBeenCalledWith({ searchTerm: valueChangeMockEvent.target.value.toLowerCase(), showTypeAhead: mockReturnValue });
    });

    it('calls onInputChange if shouldShowTypeAhead = true', () => {
      const { props, wrapper } = setup();
      shouldShowTypeAheadSpy = jest.spyOn(wrapper.instance(), 'shouldShowTypeAhead').mockImplementation(() => true);
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueChange(valueChangeMockEvent);
      expect(props.onInputChange).toHaveBeenCalledWith(valueChangeMockEvent.target.value.toLowerCase());
    });

    it('does not call onInputChange if shouldShowTypeAhead = false', () => {
      const { props, wrapper } = setup();
      shouldShowTypeAheadSpy = jest.spyOn(wrapper.instance(), 'shouldShowTypeAhead').mockImplementation(() => false);
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueChange(valueChangeMockEvent);
      expect(props.onInputChange).not.toHaveBeenCalled();
    });
  });

  describe('handleValueSubmit', () => {
    let props;
    let wrapper;
    let hideTypeAheadSpy;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('calls event.preventDefault', () => {
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(submitMockEvent.preventDefault).toHaveBeenCalled();
    });

    it('submits with correct props if isFormValid()', () => {
      const { props, wrapper } = setup({ searchTerm: 'testTerm' });
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(props.submitSearch).toHaveBeenCalledWith(props.searchTerm);
    });

    it('calls hideTypeAhead if isFormValid()', () => {
      const { props, wrapper } = setup({ searchTerm: 'testTerm' });
      hideTypeAheadSpy = jest.spyOn(wrapper.instance(), 'hideTypeAhead');
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(hideTypeAheadSpy).toHaveBeenCalled();
    });

    it('does not submit if !isFormValid()', () => {
      const { props, wrapper } = setup({ searchTerm: 'tag:tag1 tag:tag2' });
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(props.submitSearch).not.toHaveBeenCalled();
    });

    it('does not call hideTypeAhead if !isFormValid()', () => {
      const { props, wrapper } = setup({ searchTerm: 'tag:tag1 tag:tag2' });
      hideTypeAheadSpy = jest.spyOn(wrapper.instance(), 'hideTypeAhead');
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(hideTypeAheadSpy).not.toHaveBeenCalled();
    });
  });

  describe('hideTypeAhead', () => {
    it('sets shouldShowTypeAhead to false', () => {
      setStateSpy.mockClear();
      const wrapper = setup().wrapper;
      wrapper.instance().hideTypeAhead();
      expect(setStateSpy).toHaveBeenCalledWith({ showTypeAhead: false });
    });
  });

  describe('shouldShowTypeAhead', () => {
    it('returns true for non-zero length string', () => {
      const wrapper = setup().wrapper;
      expect(wrapper.instance().shouldShowTypeAhead('test')).toEqual(true);
    });

    it('returns false for empty string', () => {
      const wrapper = setup().wrapper;
      expect(wrapper.instance().shouldShowTypeAhead('')).toEqual(false);
    });
  });

  describe('onSelectInlineResult', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });
    it('calls hideTypeAhead', () => {
      const hideTypeAheadSpy = jest.spyOn(wrapper.instance(), 'hideTypeAhead');
      wrapper.update();
      wrapper.instance().onSelectInlineResult(ResourceType.table, false);
      expect(hideTypeAheadSpy).toHaveBeenCalled();
    });

    it('calls props.onSelectInlineResult with given parameters', () => {
      const givenResource = ResourceType.user;
      const givenBoolean = true;
      wrapper.instance().onSelectInlineResult(givenResource, givenBoolean);
      expect(props.onSelectInlineResult).toHaveBeenCalledWith(givenResource, wrapper.state().searchTerm, givenBoolean);
    });
  });


  describe('updateTypeAhead', () => {
    /* TODO: How to test? */
  });

  describe('isFormValid', () => {
    describe('if searchTerm has more than one category', () => {
      let wrapper;
      beforeAll(() => {
        wrapper = setup().wrapper;
      });

      it('does not accept multiple search categories', () => {
        expect(wrapper.instance().isFormValid('tag:tag1 tag:tag2')).toEqual(false);
      });

      it('does not accept empty search term', () => {
        expect(wrapper.instance().isFormValid('')).toEqual(false);
      });

      it('sets state.subText correctly', () => {
        expect(wrapper.state().subText).toEqual(SYNTAX_ERROR_CATEGORY);
      });

      it('sets state.subTextClassName correctly', () => {
        expect(wrapper.state().subTextClassName).toEqual(ERROR_CLASSNAME);
      });
    });

    describe('if searchTerm has incorrect colon syntax', () => {
      let wrapper;
      beforeAll(() => {
        wrapper = setup({ searchTerm: 'tag : tag1' }).wrapper;
      });

      it('returns false', () => {
        expect(wrapper.instance().isFormValid('tag : tag1')).toEqual(false);
      });

      it('sets state.subText correctly', () => {
        expect(wrapper.state().subText).toEqual(`${SYNTAX_ERROR_PREFIX}'tag:tag1'${SYNTAX_ERROR_SPACING_SUFFIX}`);
      });

      it('sets state.subTextClassName correctly', () => {
        expect(wrapper.state().subTextClassName).toEqual(ERROR_CLASSNAME);
      });
    });

    describe('if searchTerm has correct syntax', () => {
      let wrapper;
      beforeAll(() => {
        wrapper = setup().wrapper;
      });

      it('returns true', () => {
        expect(wrapper.instance().isFormValid('tag:tag1')).toEqual(true);
      });

      it('sets state.subText correctly', () => {
        expect(wrapper.state().subText).toEqual(SUBTEXT_DEFAULT);
      });

      it('sets state.subTextClassName correctly', () => {
        expect(wrapper.state().subTextClassName).toEqual('');
      });
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    describe('form', () => {
      it('renders with correct props', () => {
        expect(wrapper.find('form').props()).toMatchObject({
          className: 'search-bar-form',
          onSubmit: wrapper.instance().handleValueSubmit,
        });
      });

      it('renders input with correct default props', () => {
        expect(wrapper.find('form').find('input').props()).toMatchObject({
          'aria-label': SearchBar.defaultProps.placeholder,
          autoFocus: true,
          className: 'h2 large search-bar-input form-control',
          id: 'search-input',
          onChange: wrapper.instance().handleValueChange,
          placeholder: SearchBar.defaultProps.placeholder,
          value: wrapper.state().searchTerm,
        });
      });

      it('renders input with correct given props', () => {
        const { props, wrapper } = setup({ placeholder: 'Type something to search', searchTerm: 'data' });
        expect(wrapper.find('form').find('input').props()).toMatchObject({
          'aria-label': props.placeholder,
          autoFocus: true,
          className: 'h2 large search-bar-input form-control',
          id: 'search-input',
          onChange: wrapper.instance().handleValueChange,
          placeholder: props.placeholder,
          value: wrapper.state().searchTerm,
        });
      });

      describe('submit button', () => {
        it('renders button with correct props', () => {
          expect(wrapper.find('form').find('button').props()).toMatchObject({
            className: 'btn btn-flat-icon search-button large',
            type: 'submit',
          });
        });

        it('renders button img with correct props', () => {
          expect(wrapper.find('form').find('button').find('img').props()).toMatchObject({
            className: 'icon icon-search',
          });
        });
      });
    });

    describe('subtext', () =>{
      it('renders div with correct class', () => {
        expect(wrapper.children().at(1).props()).toMatchObject({
          className: `subtext body-secondary-3 ${wrapper.state().subTextClassName}`,
        });
      });

      it('renders correct text', () => {
        expect(wrapper.children().at(1).text()).toEqual(wrapper.state().subText);
      });
    });

    describe('render with small mode', () => {
      const { wrapper, props } = setup({ size: "small" });

      it('does not render a subtext', () => {
        const subtext = wrapper.find('subtext');
        expect(subtext.exists()).toBe(false);
      });

      it('renders a close button', () => {
        const closeButton = wrapper.find('button.clear-button');
        expect(closeButton.exists()).toBe(true);
        const buttonProps = closeButton.props();
        expect(buttonProps.onClick).toEqual(wrapper.instance().clearSearchTerm);
      });
    });
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets submitSearch on the props', () => {
    expect(result.submitSearch).toBeInstanceOf(Function);
  });
  it('sets onInputChange on the props', () => {
    expect(result.onInputChange).toBeInstanceOf(Function);
  });
  it('sets onSelectInlineResult on the props', () => {
    expect(result.onSelectInlineResult).toBeInstanceOf(Function);
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;
  beforeAll(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets searchAll on the props', () => {
    expect(result.submitSearch).toBeInstanceOf(Function);
  });
});

describe('mapStateToProps', () => {
  let result;
  beforeAll(() => {
    result = mapStateToProps(globalState);
  });

  it('sets searchTerm on the props', () => {
    expect(result.searchTerm).toEqual(globalState.search.search_term);
  });
});
