import * as React from 'react';

import { shallow } from 'enzyme';

import QueryList, { QueryListProps } from './';

describe('QueryList', () => {
  const setup = (propOverrides?: Partial<QueryListProps>) => {
    const props = {
      queries: [],
      ...propOverrides,
    };
    const wrapper = shallow<QueryList>(<QueryList {...props} />)
    return { props, wrapper };
  };

  describe('render', () => {
    it('returns null if no queries', () => {
      const { props, wrapper } = setup({ queries: [] });
      expect(wrapper.type()).toEqual(null);
    });

    it('returns a list item for each query', () => {
      const { props, wrapper } = setup({ queries: ['query1', 'query2'] });
      props.queries.forEach((item, index) => {
        expect(wrapper.find('li').at(index).text()).toBe(item);
      });
    });
  });
});
