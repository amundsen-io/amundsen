// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import { GlobalState } from 'ducks/rootReducer';

import globalState from 'fixtures/globalState';

import { FilterType, ResourceType } from 'interfaces';

import InfoButton from 'components/InfoButton';
import { FilterSection, FilterSectionProps, mapStateToProps } from '.';

const setup = (propOverrides?: Partial<FilterSectionProps>) => {
  const props: FilterSectionProps = {
    categoryId: 'testId',
    hasValue: true,
    title: 'Category',
    type: FilterType.INPUT_SELECT,
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = shallow<FilterSection>(<FilterSection {...props} />);
  return {
    props,
    wrapper,
  };
};

describe('FilterSection', () => {
  describe('renderFilterComponent', () => {
    it('returns an InputFilter w/ correct props if props.type == FilterType.INPUT_SELECT', () => {
      const { props, wrapper } = setup({ type: FilterType.INPUT_SELECT });
      const content = wrapper.instance().renderFilterComponent();

      expect(content?.type.displayName).toBe('Connect(InputFilter)');
      expect(content?.props.categoryId).toBe(props.categoryId);
    });

    it('returns a CheckBoxFilter w/ correct props if props.type == FilterType.CHECKBOX_SELECT', () => {
      const mockOptions = [{ label: 'hive', value: 'Hive' }];
      const { props, wrapper } = setup({
        type: FilterType.CHECKBOX_SELECT,
        options: mockOptions,
      });
      const content = wrapper.instance().renderFilterComponent();

      expect(content?.type.displayName).toBe('Connect(CheckBoxFilter)');
      expect(content?.props.categoryId).toBe(props.categoryId);
      expect(content?.props.checkboxProperties).toBe(mockOptions);
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    let renderFilterComponentSpy;

    beforeAll(() => {
      ({ props, wrapper } = setup());
      renderFilterComponentSpy = jest.spyOn(
        wrapper.instance(),
        'renderFilterComponent'
      );
    });

    it('renders FilterSection title', () => {
      expect(wrapper.find('.title-2').text()).toEqual(props.title);
    });

    it('renders InfoButton with correct props if props.helpText exists', () => {
      const mockHelpText = 'Help me';
      const { wrapper: wrapperWithHelpText } = setup({
        helpText: mockHelpText,
      });
      const infoButton = wrapperWithHelpText.find(InfoButton);

      expect(infoButton.exists()).toBe(true);
      expect(infoButton.props().infoText).toBe(mockHelpText);
    });

    it('calls renderFilterComponent()', () => {
      renderFilterComponentSpy.mockClear();
      wrapper.instance().forceUpdate();
      expect(renderFilterComponentSpy).toHaveBeenCalledTimes(1);
    });
  });

  describe('mapStateToProps', () => {
    const mockStateWithFilters: GlobalState = {
      ...globalState,
      search: {
        ...globalState.search,
        resource: ResourceType.table,
        filters: {
          [ResourceType.table]: {
            database: { hive: true },
            schema: 'schema_name',
          },
        },
      },
    };

    const mockStateWithOutFilters: GlobalState = {
      ...globalState,
      search: {
        ...globalState.search,
        resource: ResourceType.user,
        filters: {
          [ResourceType.table]: {},
        },
      },
    };

    let result;
    describe('sets hasValue as true', () => {
      it('when CHECKBOX_SELECT filter has value', () => {
        const { props } = setup({
          categoryId: 'database',
          type: FilterType.CHECKBOX_SELECT,
        });
        result = mapStateToProps(mockStateWithFilters, props);
        expect(result.hasValue).toBe(true);
      });

      it('when INPUT_SELECT filter has value', () => {
        const { props } = setup({
          categoryId: 'schema',
          type: FilterType.INPUT_SELECT,
        });
        result = mapStateToProps(mockStateWithFilters, props);
        expect(result.hasValue).toBe(true);
      });
    });

    describe('sets hasValue as false', () => {
      it('when CHECKBOX_SELECT filter has no value', () => {
        const { props } = setup({
          categoryId: 'database',
          type: FilterType.CHECKBOX_SELECT,
        });
        result = mapStateToProps(mockStateWithOutFilters, props);
        expect(result.hasValue).toBe(false);
      });

      it('when INPUT_SELECT filter has no value', () => {
        const { props } = setup({
          categoryId: 'schema',
          type: FilterType.INPUT_SELECT,
        });
        result = mapStateToProps(mockStateWithOutFilters, props);
        expect(result.hasValue).toBe(false);
      });

      it('when no filters exist for the given category', () => {
        const { props } = setup({ categoryId: 'fakeCategory' });
        result = mapStateToProps(mockStateWithFilters, props);
        expect(result.hasValue).toEqual(false);
      });
    });
  });
});
