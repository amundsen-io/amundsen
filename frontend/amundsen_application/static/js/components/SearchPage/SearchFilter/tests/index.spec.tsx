import * as React from 'react';
import { shallow } from 'enzyme';

import { mapStateToProps, mapDispatchToProps, SearchFilter, SearchFilterProps} from '../';

import CheckBoxItem from 'components/common/Inputs/CheckBoxItem';

describe('SearchFilter', () => {
  const setup = (propOverrides?: Partial<SearchFilterProps>) => {
    const props = {
      checkBoxSections: [
        {
          title: 'Type',
          categoryId: 'datasets',
          inputProperties: [
            {
              value: 'bigquery',
              labelText: 'BigQuery',
              checked: true,
              count: 100,
            },
            {
              value: 'hive',
              labelText: 'Hive',
              checked: true,
              count: 100,
            },
            {
              value: 'druid',
              labelText: 'Druid',
              checked: true,
              count: 0,
            },
            {
              value: 's3',
              labelText: 'S3 Buckets',
              checked: false,
              count: 100,
            }
          ]
        }
      ],
      onFilterChange: jest.fn(),
      ...propOverrides
    };
    const wrapper = shallow<SearchFilter>(<SearchFilter {...props} />);
    return { props, wrapper };
  };

  describe('createCheckBoxItem', () => {
    let props;
    let wrapper;

    let itemData;
    let categoryId;
    let content;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      itemData = props.checkBoxSections[0].inputProperties[0];
      categoryId = 'testId'
      content = shallow(wrapper.instance().createCheckBoxItem(itemData, categoryId, 'itemKey'));
    });
    /*
    TODO: Enzyme might not allow this kind of check with shallow rendering.
    Revisit on final implementation
    it('returns CheckBoxItem with correct props', () => {
      expect(content.type()).toEqual(CheckBoxItem);
    });
    */
    it('renders labelText as first CheckBoxItem child', () => {
      const child = content.find('span').at(0);
      expect(child.hasClass('subtitle-2')).toBe(true);
      expect(child.text()).toEqual(itemData.labelText);
    });

    it('renders count as second CheckBoxItem child', () => {
      const child = content.find('span').at(1);
      expect(child.hasClass('body-secondary-3 pull-right')).toBe(true);
      expect(child.text()).toEqual(itemData.count.toString());
    });
  });

  describe('createCheckBoxSection', () => {
    let props;
    let wrapper;

    let content;
    let sectionData;
    let createCheckBoxItemSpy;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      createCheckBoxItemSpy = jest.spyOn(wrapper.instance(), 'createCheckBoxItem');
      sectionData = props.checkBoxSections[0];
      content = shallow(wrapper.instance().createCheckBoxSection(sectionData, 'sectionKey'));
    });
    it('render content with correct class', () => {
      expect(content.hasClass('search-filter-section')).toBe(true);
    });

    it('renders correct title', () => {
      const title = content.children().at(0);
      expect(title.hasClass('title-2')).toBe(true);
      expect(title.text()).toEqual(sectionData.title);
    });

    it('calls createCheckBoxItem for each section.inputProperties', () => {
      createCheckBoxItemSpy.mockClear();
      wrapper.instance().createCheckBoxSection(sectionData, 'sectionKey');
      const { categoryId } = sectionData;
      sectionData.inputProperties.forEach((item, index ) => {
        expect(createCheckBoxItemSpy).toHaveBeenCalledWith(item, categoryId, `item:${categoryId}:${index}`);
      });
      expect(createCheckBoxItemSpy).toHaveBeenCalledTimes(sectionData.inputProperties.length);
    });
  });

  describe('render', () => {
    let props;
    let wrapper;
    let createCheckBoxSectionSpy;

    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;

      createCheckBoxSectionSpy = jest.spyOn(wrapper.instance(), 'createCheckBoxSection');
    });

    it('calls createCheckBoxSection for each checkBoxSection', () => {
      createCheckBoxSectionSpy.mockClear();
      wrapper.instance().render();
      props.checkBoxSections.forEach((section, index ) => {
        expect(createCheckBoxSectionSpy).toHaveBeenCalledWith(section, `section:${index}`);
      });
      expect(createCheckBoxSectionSpy).toHaveBeenCalledTimes(props.checkBoxSections.length);
    });
  });
});

describe('mapStateToProps', () => {
  // TODO
});

describe('mapDispatchToProps', () => {
  // TODO
});
