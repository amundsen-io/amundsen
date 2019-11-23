import * as React from 'react';

import { shallow } from 'enzyme';

import SearchItem, { SearchItemProps } from '../';

import { ResourceType } from 'interfaces';

import { logClick } from 'ducks/utilMethods';
jest.mock('ducks/utilMethods', () => (
  {
    logClick: jest.fn(() => {}),
  }
));

describe('SearchItem', () => {
  const setup = (propOverrides?: Partial<SearchItemProps>) => {
    const props: SearchItemProps = {
      listItemText: 'test',
      onItemSelect: jest.fn(),
      searchTerm: 'test search',
      resourceType: ResourceType.table,
      ...propOverrides
    };
    const wrapper = shallow<SearchItem>(<SearchItem {...props} />);
    return { props, wrapper };
  };

  describe('onViewAllResults', () => {
    it('calls props.onItemSelect with the correct parameters', () => {
      const { props, wrapper } = setup();
      const onItemSelectSpy = jest.spyOn(props, 'onItemSelect');
      wrapper.instance().onViewAllResults({});
      expect(onItemSelectSpy).toHaveBeenCalledWith(props.resourceType, true);
    })
  });

  describe('render', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setUpResult = setup();
      props = setUpResult.props;
      wrapper = setUpResult.wrapper;
    });

    describe('renders list item link', () => {
      let listItemLink;
      beforeAll(() => {
        listItemLink = wrapper.find('li').find('a');
      });

      it('with correct onClick interaction', () => {
        expect(listItemLink.props().onClick).toBe(wrapper.instance().onViewAllResults);
      });

      it('with correct class', () => {
        expect(listItemLink.hasClass('search-item-link')).toBe(true);
      });

      describe('with correct content', () => {
        it('renders an img with correct class', () => {
          expect(listItemLink.find('img').props().className).toEqual('icon icon-search');
        });

        it('renders correct text', () => {
          expect(listItemLink.text()).toEqual(`${props.searchTerm}\u00a0${props.listItemText}`);
        });
      });
    });
  });
});
