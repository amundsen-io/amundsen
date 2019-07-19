import * as React from 'react';

import { shallow } from 'enzyme';

import LoadingSpinner from 'components/common/LoadingSpinner';
import { TagsList, TagsListProps, mapDispatchToProps, mapStateToProps } from '../';

import globalState from 'fixtures/globalState';

import AppConfig from 'config/config';
AppConfig.browse.curatedTags = ['test1'];

describe('TagsList', () => {
  let props: TagsListProps;
  let subject;

  beforeEach(() => {
    props = {
      allTags: [
        {
          tag_count: 2,
          tag_name: 'test1',
        },
        {
          tag_count: 1,
          tag_name: 'test2',
        },
      ],
      isLoading: false,
      getAllTags: jest.fn(),
    };
    subject = shallow(<TagsList {...props} />);
  });

  describe('getDerivedStateFromProps', () => {
    it('returns correct state if props.isLoading', () => {
      const prevState = subject.state();
      props.isLoading = true;
      subject.setProps(props);
      expect(subject.state()).toMatchObject({
        ...prevState,
        isLoading: true,
      });
    });

    it('returns correct state if !props.isLoading', () => {
      props.isLoading = false;
      subject.setProps(props);
      expect(subject.state()).toMatchObject({
        curatedTags: [{ tag_count: 2, tag_name: 'test1'}],
        otherTags: [{ tag_count: 1, tag_name: 'test2'}],
        isLoading: false,
      });
    });

    it('returns correct state if !props.isLoading and !AppConfig.browse.showAllTags', () => {
      AppConfig.browse.showAllTags = false;
      subject = shallow(<TagsList {...props} />);
      expect(subject.state()).toMatchObject({
        curatedTags: [{tag_count: 2, tag_name: 'test1'}],
        otherTags: [],
        isLoading: false,
      });
      AppConfig.browse.showAllTags = true; // reset so other tests aren't affected
    });
  });

  describe('componentDidMount', () => {
      it('calls props.getAllTags', () => {
          expect(props.getAllTags).toHaveBeenCalled();
      });
  });

  describe('render', () => {
    let spy;
    beforeEach(() => {
      spy = jest.spyOn(TagsList.prototype, 'generateTagInfo');
    });
    it('renders LoadingSpinner if state.isLoading', () => {
      /* Note: For some reason setState is not updating the component in this case */
      props.isLoading = true;
      subject.setProps(props);
      expect(subject.find(LoadingSpinner).exists()).toBeTruthy();
    });

    it('renders <hr> in if curatedTags.length > 0 & otherTags.length > 0 ', () => {
      expect(subject.find('#browse-body').find('hr').exists()).toBeTruthy();
    });

    it('does not render <hr> if !(curatedTags.length > 0 & otherTags.length > 0) ', () => {
      AppConfig.browse.curatedTags = ['test1', 'test2'];
      subject = shallow(<TagsList {...props} />);
      expect(subject.find('#browse-body').find('hr').exists()).toBeFalsy();
      AppConfig.browse.curatedTags = ['test1']; // reset so other tests aren't affected
    });

    it('calls generateTagInfo with curatedTags', () => {
      expect(spy).toHaveBeenCalledWith(subject.state().curatedTags);
    });

    it('call generateTagInfo with otherTags', () => {
      expect(spy).toHaveBeenCalledWith(subject.state().otherTags);
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
  beforeEach(() => {
    result = mapStateToProps(globalState);
  });

  it('sets allTags on the props', () => {
    expect(result.allTags).toEqual(globalState.allTags.allTags);
  });

  it('sets isLoading on the props', () => {
    expect(result.isLoading).toEqual(globalState.allTags.isLoading);
  });
});
