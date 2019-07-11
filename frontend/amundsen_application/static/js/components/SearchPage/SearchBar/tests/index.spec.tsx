import * as React from 'react';

import { shallow } from 'enzyme';

import { mapStateToProps, SearchBar, SearchBarProps } from '../';
import {
  ERROR_CLASSNAME,
  SUBTEXT_DEFAULT,
  SYNTAX_ERROR_CATEGORY,
  SYNTAX_ERROR_PREFIX,
  SYNTAX_ERROR_SPACING_SUFFIX,
} from '../constants';
import globalState from 'fixtures/globalState';
import { getMockRouterProps } from 'fixtures/mockRouter';

describe('SearchBar', () => {
  const valueChangeMockEvent = { target: { value: 'Data Resources' } };
  const submitMockEvent = { preventDefault: jest.fn() };
  const setStateSpy = jest.spyOn(SearchBar.prototype, 'setState');
  const routerProps = getMockRouterProps<any>(null, null);
  const historyPushSpy = jest.spyOn(routerProps.history, 'push');
  const setup = (propOverrides?: Partial<SearchBarProps>) => {
    const props: SearchBarProps = {
      searchTerm: '',
      ...routerProps,
      ...propOverrides
    };
    const wrapper = shallow<SearchBar>(<SearchBar {...props} />)
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

  describe('getDerivedStateFromProps', () => {
    it('sets searchTerm on state from props', () => {
      const { props, wrapper } = setup();
      const prevState = wrapper.state();
      props.searchTerm = 'newTerm';
      wrapper.setProps(props);
      expect(wrapper.state()).toMatchObject({
        ...prevState,
        searchTerm: 'newTerm',
      });
    });
  });

  describe('handleValueChange', () => {
    it('calls setState on searchTerm with event.target.value.toLowerCase()', () => {
      const { props, wrapper } = setup();
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueChange(valueChangeMockEvent);
      expect(setStateSpy).toHaveBeenCalledWith({ searchTerm: valueChangeMockEvent.target.value.toLowerCase() });
    });
  });

  describe('handleValueSubmit', () => {
    let props;
    let wrapper;
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

    it('redirects back to home if searchTerm is empty', () => {
      historyPushSpy.mockClear();
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(historyPushSpy).toHaveBeenCalledWith('/');
    });

    it('submits with correct props if isFormValid()', () => {
      historyPushSpy.mockClear();
      const { props, wrapper } = setup({ searchTerm: 'testTerm' });
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(historyPushSpy).toHaveBeenCalledWith(`/search?searchTerm=${wrapper.state().searchTerm}`);
    });

    it('does not submit if !isFormValid()', () => {
      historyPushSpy.mockClear();
      const { props, wrapper } = setup({ searchTerm: 'tag:tag1 tag:tag2' });
      // @ts-ignore: mocked events throw type errors
      wrapper.instance().handleValueSubmit(submitMockEvent);
      expect(historyPushSpy).not.toHaveBeenCalled();
    });
  });

  describe('isFormValid', () => {
    describe('if searchTerm has more than one category', () => {
      let wrapper;
      beforeAll(() => {
        wrapper = setup().wrapper;
      })

      it('returns false', () => {
        expect(wrapper.instance().isFormValid('tag:tag1 tag:tag2')).toEqual(false);
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
      })

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
      })

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
          className: 'h2 search-bar-input form-control',
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
          className: 'h2 search-bar-input form-control',
          id: 'search-input',
          onChange: wrapper.instance().handleValueChange,
          placeholder: props.placeholder,
          value: wrapper.state().searchTerm,
        });
      });

      describe('submit button', () => {
        it('renders button with correct props', () => {
          expect(wrapper.find('form').find('button').props()).toMatchObject({
            className: 'btn btn-flat-icon search-bar-button',
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
