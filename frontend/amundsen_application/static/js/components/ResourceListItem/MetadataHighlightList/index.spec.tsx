// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';
import { TableIcon } from 'components/SVGIcons';
import MetadataHighlightList, { MetadataHighlightListProps } from '.';

describe('MetadataHighlightList', () => {
  const setup = (propOverrides?: Partial<MetadataHighlightListProps>) => {
    const props: MetadataHighlightListProps = {
      fieldName: 'columns test field',
      highlightedMetadataList: 'column1, column2, column3',
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = mount(<MetadataHighlightList {...props} />);
    return {
      props,
      wrapper,
    };
  };
  describe('render', () => {
    let props: MetadataHighlightListProps;
    let wrapper;

    beforeAll(() => {
      ({ props, wrapper } = setup());
    });

    it('renders correct icon', () => {
      const actual = wrapper.find(TableIcon).length;
      const expected = 1;

      expect(actual).toEqual(expected);
    });
    it('renders highlighted content', () => {
      const actual = wrapper.find('.highlight-content').text();
      const expected = `Matching ${props.fieldName}: ${props.highlightedMetadataList}`;

      expect(actual).toEqual(expected);
    });
  });
});
