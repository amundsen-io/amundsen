import * as React from 'react';

import { shallow } from 'enzyme';

import LoadingSpinner from 'components/common/LoadingSpinner';
import { TagsList, TagsListProps, mapDispatchToProps, mapStateToProps } from '../';

import globalState from 'fixtures/globalState';

import AppConfig from 'config/config';
AppConfig.browse.curatedTags = ['test1'];

jest.mock('config/config-utils', () => (
  {
    showAllTags: jest.fn(),
    getCuratedTags: () => { return ['curated_tag_1']; },
  }
));

import { getCuratedTags, showAllTags } from 'config/config-utils';


describe('TagsList', () => {

  const setup = (propOverrides?: Partial<TagsListProps>) => {
    const props: TagsListProps = {
      curatedTags: [
        {
          tag_count: 2,
          tag_name: 'test1',
        },
      ],
      otherTags: [
        {
          tag_count: 1,
          tag_name: 'test2',
        },
      ],
      isLoading: false,
      getAllTags: jest.fn(),
      ...propOverrides,
    };

    const wrapper = shallow(<TagsList {...props} />);
    return { props, wrapper };
  };

  describe('componentDidMount', () => {
    it('calls props.getAllTags', () => {
      const { props, wrapper } = setup();
      expect(props.getAllTags).toHaveBeenCalled();
    });
  });

  describe('render', () => {
    it('renders LoadingSpinner if props.isLoading is true', () => {
      const { props, wrapper } = setup({ isLoading: true });
      expect(wrapper.find(LoadingSpinner).exists()).toBe(true);
    });

    it('renders <hr> if curatedTags.length > 0 & otherTags.length > 0 & showAllTags == true', () => {
      // @ts-ignore
      showAllTags.mockImplementation(() => true);
      const { props, wrapper } = setup();
      expect(wrapper.find('hr').exists()).toBe(true);
    });

    it('does not render <hr> if showAllTags is false', () => {
      // @ts-ignore
      showAllTags.mockImplementation(() => false);
      const { props, wrapper } = setup();
      expect(wrapper.find('hr').exists()).toBe(false);
    });

    it('does not render an <hr> if otherTags is empty', () => {
      // @ts-ignore
      showAllTags.mockImplementation(() => true);
      const { props, wrapper } = setup();

      expect(wrapper.find('#tags-list').find('hr').exists()).toBe(true);
    });

    it('calls generateTagInfo with curatedTags', () => {
      const generateTagInfoSpy = jest.spyOn(TagsList.prototype, 'generateTagInfo');
      const { props, wrapper } = setup();
      expect(generateTagInfoSpy).toHaveBeenCalledWith(props.curatedTags)
    });

    it('call generateTagInfo with otherTags', () => {
      const generateTagInfoSpy = jest.spyOn(TagsList.prototype, 'generateTagInfo');
      const { props, wrapper } = setup();
      expect(generateTagInfoSpy).toHaveBeenCalledWith(props.otherTags)
    });
  });
});

describe('mapDispatchToProps', () => {
  let dispatch;
  let result;

  beforeEach(() => {
    dispatch = jest.fn(() => Promise.resolve());
    result = mapDispatchToProps(dispatch);
  });

  it('sets getAllTags on the props', () => {
    expect(result.getAllTags).toBeInstanceOf(Function);
  });
});

describe('mapStateToProps', () => {
  let result;
  let expectedCuratedTags;
  let expectedOtherTags;
  beforeEach(() => {
    result = mapStateToProps(globalState);
    const allTags = globalState.allTags.allTags;
    const curatedTagsList = getCuratedTags();
    expectedCuratedTags = allTags.filter((tag) => curatedTagsList.indexOf(tag.tag_name) !== -1);
    expectedOtherTags = allTags.filter((tag) => curatedTagsList.indexOf(tag.tag_name) === -1);
  });

  it('sets curatedTags on the props', () => {
    expect(result.curatedTags).toEqual(expectedCuratedTags);
  });

  it('sets otherTags on the props', () => {
    expect(result.otherTags).toEqual(expectedOtherTags);
  });

  it('sets isLoading on the props', () => {
    expect(result.isLoading).toEqual(globalState.allTags.isLoading);
  });
});
