import * as React from 'react';

import { mocked } from 'ts-jest/utils';
import { shallow } from 'enzyme';

import SearchItemList, { SearchItemListProps } from '../';
import SearchItem from '../SearchItem';

import { ResourceType } from 'interfaces';

import * as CONSTANTS from '../../constants';

jest.mock('config/config-utils', () => ({
  getDisplayNameByResource: jest.fn(),
  indexUsersEnabled: jest.fn()
}));
import { indexUsersEnabled } from 'config/config-utils';

jest.mock("react-redux", () => {
  return {
    connect: (mapStateToProps, mapDispatchToProps) => (
      SearchItem
    ) => SearchItem
  };
});

describe('SearchItemList', () => {
  const setup = (propOverrides?: Partial<SearchItemListProps>) => {
    const props: SearchItemListProps = {
      onItemSelect: jest.fn(),
      searchTerm: 'test',
      ...propOverrides
    };
    const wrapper = shallow<SearchItemList>(<SearchItemList {...props} />);
    return { props, wrapper };
  };

  describe('getListItemText', () => {
    let wrapper;
    beforeAll(() => {
      wrapper = setup().wrapper;
    });

    it('returns the correct value for ResourceType.table', () => {
      const output = wrapper.instance().getListItemText(ResourceType.table);
      expect(output).toEqual(CONSTANTS.DATASETS_ITEM_TEXT);
    });

    it('returns the correct value for ResourceType.user', () => {
      const output = wrapper.instance().getListItemText(ResourceType.user);
      expect(output).toEqual(CONSTANTS.PEOPLE_ITEM_TEXT);
    });

    it('returns empty string as the default', () => {
      const output = wrapper.instance().getListItemText('unsupported');
      expect(output).toEqual('');
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    let setUpResult;
    let getListItemTextSpy;
    let mockListItemText;

    it('renders a SearchItem for ResourceType.table', () => {
      setUpResult = setup();
      props = setUpResult.props;
      wrapper = setUpResult.wrapper;
      mockListItemText = 'Hello'
      getListItemTextSpy = jest.spyOn(wrapper.instance(), 'getListItemText').mockImplementation(() => mockListItemText);
      wrapper.instance().forceUpdate();

      const item = wrapper.find('SearchItem').findWhere(item => item.prop('resourceType') === ResourceType.table);
      const itemProps = item.props();
      expect(getListItemTextSpy).toHaveBeenCalledWith(ResourceType.table);
      expect(itemProps.listItemText).toEqual(mockListItemText);
      expect(itemProps.onItemSelect).toEqual(props.onItemSelect);
      expect(itemProps.searchTerm).toEqual(props.searchTerm);
      expect(itemProps.resourceType).toEqual(ResourceType.table);
    });

    describe('renders ResourceType.user SearchItem based on config', () =>{
      it('when indexUsersEnabled = true, renders SearchItem', () => {
        mocked(indexUsersEnabled).mockImplementation(() => true);
        setUpResult = setup();
        props = setUpResult.props;
        wrapper = setUpResult.wrapper;
        mockListItemText = 'Hello'
        getListItemTextSpy = jest.spyOn(wrapper.instance(), 'getListItemText').mockImplementation(() => mockListItemText);
        wrapper.instance().forceUpdate();

        const item = wrapper.find('SearchItem').findWhere(item => item.prop('resourceType') === ResourceType.user);
        const itemProps = item.props();
        expect(getListItemTextSpy).toHaveBeenCalledWith(ResourceType.user);
        expect(itemProps.listItemText).toEqual(mockListItemText);
        expect(itemProps.onItemSelect).toEqual(props.onItemSelect);
        expect(itemProps.searchTerm).toEqual(props.searchTerm);
        expect(itemProps.resourceType).toEqual(ResourceType.user);
      });

      it('when indexUsersEnabled = false, does not render SearchItem', () => {
        mocked(indexUsersEnabled).mockImplementation(() => false);
        wrapper = setup().wrapper;
        const item = wrapper.find('SearchItem').findWhere(item => item.prop('resourceType') === ResourceType.user);
        expect(item.exists()).toBe(false)
      })
    });
  });
});
