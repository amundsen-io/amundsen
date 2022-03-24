// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import { FilterType } from 'interfaces';

import InfoButton from 'components/InfoButton';
import InputFilter from '../InputFilter';
import CheckBoxFilter from '../CheckBoxFilter';
import FilterSection, { FilterSectionProps } from '.';

const setup = (propOverrides?: Partial<FilterSectionProps>) => {
  const props: FilterSectionProps = {
    categoryId: 'testId',
    title: 'Category',
    type: FilterType.INPUT_SELECT,
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = shallow<typeof FilterSection>(<FilterSection {...props} />);
  return {
    props,
    wrapper,
  };
};

describe('FilterSection', () => {
  describe('getFilterComponent', () => {
    it('returns an InputFilter w/ correct props if props.type == FilterType.INPUT_SELECT', () => {
      const { props, wrapper } = setup({ type: FilterType.INPUT_SELECT });
      const { categoryId } = props;

      const inputFilter = wrapper.childAt(1).dive().find(InputFilter);
      const expectedLength = 1;

      expect(inputFilter.length).toBe(expectedLength);
      expect(inputFilter.prop('categoryId')).toBe(categoryId);
    });

    it('returns a CheckBoxFilter w/ correct props if props.type == FilterType.CHECKBOX_SELECT', () => {
      const mockOptions = [{ label: 'hive', value: 'Hive' }];
      const { props, wrapper } = setup({
        type: FilterType.CHECKBOX_SELECT,
        options: mockOptions,
      });
      const { categoryId } = props;

      const checkboxFilter = wrapper.childAt(1).dive().find(CheckBoxFilter);
      const expectedLength = 1;

      expect(checkboxFilter.length).toBe(expectedLength);
      expect(checkboxFilter.prop('categoryId')).toBe(categoryId);
      expect(checkboxFilter.prop('checkboxProperties')).toEqual(mockOptions);
    });
  });

  describe('render', () => {
    let props;
    let wrapper;

    beforeAll(() => {
      ({ props, wrapper } = setup());
    });

    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    it('renders FilterSection title', () => {
      expect(
        wrapper.childAt(0).dive().find('.search-filter-section-label').text()
      ).toEqual(props.title);
    });

    it('renders InfoButton with correct props if props.helpText exists and it is a checkbox filter type', () => {
      const mockHelpText = 'Help me';
      const { wrapper: wrapperWithHelpText } = setup({
        type: FilterType.CHECKBOX_SELECT,
        helpText: mockHelpText,
      });
      const infoButton = wrapperWithHelpText.childAt(0).dive().find(InfoButton);

      expect(infoButton.exists()).toBeTruthy();
      expect(infoButton.props().infoText).toBe(mockHelpText);
    });

    it('does not render InfoButton if props.helpText exists and it is an input filter type', () => {
      const mockHelpText = 'Help me';
      const { wrapper: wrapperWithHelpText } = setup({
        type: FilterType.INPUT_SELECT,
        helpText: mockHelpText,
      });
      const infoButton = wrapperWithHelpText.childAt(0).dive().find(InfoButton);

      expect(infoButton.exists()).toBeFalsy();
    });
  });
});
