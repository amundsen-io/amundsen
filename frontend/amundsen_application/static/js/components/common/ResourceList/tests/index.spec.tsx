import * as React from 'react';
import Pagination from 'react-js-pagination';

import { shallow } from 'enzyme';

import { ResourceType } from 'interfaces';
import ResourceListItem from 'components/common/ResourceListItem/index';
import ResourceList, { ResourceListProps } from '../';

import * as CONSTANTS from '../constants';

describe('ResourceList', () => {
  const setStateSpy = jest.spyOn(ResourceList.prototype, 'setState');
  const setupAllItems = (propOverrides?: Partial<ResourceListProps>) => {
    const props: ResourceListProps = {
      allItems: [
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
      ],
      itemsPerPage: 4,
      source: 'testSource',
      ...propOverrides
    };
    const wrapper = shallow<ResourceList>(<ResourceList {...props} />);
    return { props, wrapper };
  };

  const setupSlicedItems =  (propOverrides?: Partial<ResourceListProps>) => {
    const props: ResourceListProps = {
      source: 'testSource',
      activePage: 3,
      slicedItems: [
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
        { type: ResourceType.table },
      ],
      slicedItemsCount: 40,
      itemsPerPage: 4,
      onPagination: jest.fn(),
      ...propOverrides
    };
    const wrapper = shallow<ResourceList>(<ResourceList {...props} />);
    return { props, wrapper };
  };

  describe('onViewAllToggle', () => {
    it('negates state.Expanded', () => {
      const wrapper = setupAllItems().wrapper;
      const initialState = wrapper.state().isExpanded;
      wrapper.instance().onViewAllToggle();
      expect(wrapper.state().isExpanded).toEqual(!initialState);
      wrapper.instance().onViewAllToggle();
      expect(wrapper.state().isExpanded).toEqual(initialState);
    })
  })

  describe('render', () => {
    describe('renders title if it exists', () => {
      const { props, wrapper } = setupAllItems({ title: 'I am a title'});
      expect(wrapper.find('.resource-list-title').text()).toBe(props.title);
    });

    describe('renders empty messages if it exists and there are no items', () => {
      const { props, wrapper } = setupAllItems({ allItems: [], customEmptyText: 'Nothing Here'});
      expect(wrapper.find('.empty-message').text()).toBe(props.customEmptyText);
    });

    describe('renders footer', () => {
      it('renders nothing if pagination is turned on', () => {
        const { props, wrapper } = setupAllItems({ paginate: true });
        expect(wrapper.find('.resource-list-footer').children().length).toBe(0);
      });

      describe('renders toggle link if not paginating with itemsToRender.length > ITEMS_PER_PAGE', () => {
        let props;
        let wrapper;
        let footerLink;
        beforeAll(() => {
          const setupResult = setupAllItems({ paginate: false });
          props = setupResult.props;
          wrapper = setupResult.wrapper;
          footerLink = wrapper.find('.resource-list-footer').find('a');
        });

        it('renders a link to toggle viewing items', () => {
          expect(footerLink.props().onClick).toEqual(wrapper.instance().onViewAllToggle)
        });

        it('renders correct default text if not expanded', () => {
          wrapper.setState({ isExpanded: false });
          expect(wrapper.find('.resource-list-footer').find('a').text()).toEqual('View all');
        });

        it('renders customFooterText text if it exists and not expanded', () => {
          wrapper = setupAllItems({ paginate: false, customFooterText: 'Hello' }).wrapper;
          expect(wrapper.find('.resource-list-footer').find('a').text()).toEqual('Hello');
        })

        it('renders correct default text if expanded', () => {
          wrapper.setState({ isExpanded: true });
          expect(wrapper.find('.resource-list-footer').find('a').text()).toEqual('View less');
        });
      });
    });
  });

  describe('render with no pagination', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setupAllItems({ paginate: false });
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('should render all items if expanded', () => {
      wrapper.setState({ isExpanded: true });
      const items = wrapper.find(ResourceListItem);
      expect(items.length).toEqual(props.allItems.length);
    });

    it('should render items.length = itemsPerPage if not expanded', () => {
      wrapper.setState({ isExpanded: false });
      const items = wrapper.find(ResourceListItem);
      expect(items.length).toEqual(CONSTANTS.ITEMS_PER_PAGE);
    });

    it('passes correct props to each ResourceListItem', () => {
      const items = wrapper.find(ResourceListItem);
      items.forEach((contentItem, idx) => {
        expect(contentItem.props()).toMatchObject({
          item: props.allItems[idx],
          logging: {
            source: props.source,
            index: idx,
          }
        })
      });
    });
  });

  describe('render allItems', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setupAllItems();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders at most itemsPerPage ResourceListItems', () => {
      const items = wrapper.find(ResourceListItem);
      expect(items.length).toEqual(props.itemsPerPage);
    });

    it('renders a pagination widget when there are more than itemsPerPage items', () => {
      expect(wrapper.find(Pagination).exists()).toBe(true)
    });

    it('hides a pagination widget when there are fewer than itemsPerPage items', () => {
      const { props, wrapper } = setupAllItems({
        itemsPerPage: 20,
      });
      expect(wrapper.find(Pagination).exists()).toBe(false)
    });
  });

  describe('render slicedItems', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setupSlicedItems();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders all slicedItems', () => {
      const items = wrapper.find(ResourceListItem);
      expect(items.length).toEqual(props.slicedItems.length);
    });

    it('renders pagination widget when slicedItemsCount is greater than itemsPerPage', () => {
      expect(wrapper.find(Pagination).exists()).toBe(true);
    });

    it('hides pagination widget when slicedItemsCount is less than itemsPerPage', () => {
      const { props, wrapper } = setupAllItems({
        itemsPerPage: 20,
      });
      expect(wrapper.find(Pagination).exists()).toBe(false);
    });
  });

  describe('onPagination', () => {
    it('calls the onPagination prop when it exists', () => {
      const setupResult = setupSlicedItems();
      const wrapper = setupResult.wrapper;
      const props = setupResult.props;
      const onPaginationSpy = jest.spyOn(props, 'onPagination');

      wrapper.instance().onPagination(3);
      expect(onPaginationSpy).toHaveBeenCalledWith(2);
    });

    it('calls setState when onPagination prop does not exist', () => {
      setStateSpy.mockClear();
      const setupResult = setupSlicedItems({ onPagination: undefined });
      const wrapper = setupResult.wrapper;
      wrapper.instance().onPagination(3);
      expect(setStateSpy).toHaveBeenCalledWith({ activePage: 2 });
    });
  });
});
