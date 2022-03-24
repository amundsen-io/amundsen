// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import InfoButton from 'components/InfoButton';

import { ToggleSwitch } from 'components/ToggleSwitch';

import globalState from 'fixtures/globalState';

import { GlobalState } from 'ducks/rootReducer';

import { ResourceType } from 'interfaces';

import {
  ToggleFilter,
  ToggleFilterProps,
  mapDispatchToProps,
  mapStateToProps,
} from '.';

describe('ToggleFilter', () => {
  const setup = (propOverrides?: Partial<ToggleFilterProps>) => {
    const props: ToggleFilterProps = {
      categoryId: 'pii',
      filterName: 'PII',
      helpText: 'Filters out all resources cotaining PII',
      checked: true,
      applyFilters: jest.fn(),
      ...propOverrides,
    };
    // eslint-disable-next-line react/jsx-props-no-spreading
    const wrapper = shallow<ToggleFilter>(<ToggleFilter {...props} />);
    return {
      props,
      wrapper,
    };
  };

  describe('render', () => {
    it('creates ToggleSwitch', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find(ToggleSwitch).length;
      expect(actual).toEqual(expected);
    });
    it('creates filter title', () => {
      const { wrapper } = setup();
      const expected = 'PII';
      const actual = wrapper.find('.search-filter-section-label').text();
      expect(actual).toEqual(expected);
    });
    it('creates information icon if helpText is defined', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find(InfoButton).length;
      expect(actual).toEqual(expected);
    });
    it('does not create information icon if helpText is not defined', () => {
      const helpText = undefined;
      const { wrapper } = setup({ helpText });
      const expected = 0;
      const actual = wrapper.find(InfoButton).length;
      expect(actual).toEqual(expected);
    });
  });

  describe('handleChange', () => {
    it('calls props.applyFilters with expected parameters', () => {
      const { props, wrapper } = setup();
      const applyFiltersSpy = jest.spyOn(props, 'applyFilters');
      wrapper.instance().handleChange(false);
      expect(applyFiltersSpy).toHaveBeenCalledWith(props.categoryId, ['false']);
    });
  });

  describe('mapStateToProps', () => {
    const { props } = setup();
    const mockFilters = { value: 'true' };

    const mockStateWithFilters: GlobalState = {
      ...globalState,
      search: {
        ...globalState.search,
        resource: ResourceType.table,
        filters: {
          [ResourceType.table]: {
            [props.categoryId]: mockFilters,
          },
        },
      },
    };

    it('sets checked on the props with the filter value for the categoryId', () => {
      const actual = mapStateToProps(mockStateWithFilters, props);
      const expected = true;
      expect(actual.checked).toEqual(expected);
    });
  });

  describe('mapDispatchToProps', () => {
    it('sets applyFilters on the props', () => {
      const dispatch = jest.fn(() => Promise.resolve());
      const expected = mapDispatchToProps(dispatch).applyFilters;
      expect(expected).toBeInstanceOf(Function);
    });
  });
});
