import * as React from 'react';

import { shallow } from 'enzyme';

import { Resource, ResourceType } from 'components/common/ResourceListItem/types';
import ResourceListItem from 'components/common/ResourceListItem';
import SearchList, { SearchListProps, SearchListParams } from '../';

describe('SearchList', () => {
  const setup = (propOverrides?: Partial<SearchListProps>) => {
    const props: SearchListProps = {
      results: [
        { type: ResourceType.table },
        { type: ResourceType.user },
      ],
      params: {
        source: 'testSource',
        paginationStartIndex: 0,
      },
      ...propOverrides
    };
    const wrapper = shallow(<SearchList {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    let props;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    it('renders unordered list', () => {
      expect(wrapper.type()).toEqual('ul');
    });

    it('renders unordered list w/ correct className', () => {
      expect(wrapper.props()).toMatchObject({
        className: 'list-group',
      });
    });

    it('renders a ResourceListItem for each result', () => {
      const content = wrapper.find(ResourceListItem);
      expect(content.length).toEqual(props.results.length);
    });

    it('passes correct props to each ResourceListItem', () => {
      const content = wrapper.find(ResourceListItem);
      content.forEach((contentItem, index) => {
        expect(contentItem.props()).toMatchObject({
          item: props.results[index],
          logging: {
            source: props.params.source,
            index: props.params.paginationStartIndex + index,
          }
        })
      });
    });
  });
});
