import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import { Breadcrumb, BreadcrumbProps, mapStateToProps, mapDispatchToProps } from '../';
import globalState from '../../../../fixtures/globalState';

describe('Breadcrumb', () => {
  let props: BreadcrumbProps;
  let subject;

  describe('render', () => {
    beforeEach(() => {
      props = {
        path: 'testPath',
        text: 'testText',
        searchTerm: '',
        loadPreviousSearch: jest.fn(),
      };
      subject = shallow(<Breadcrumb {...props} />);
    });

    it('renders Link with correct path', () => {
      expect(subject.find(Link).props()).toMatchObject({
        to: props.path,
      });
    });

    it('renders Link with correct text', () => {
      expect(subject.find(Link).find('span').text()).toEqual(props.text);
    });
  });

  describe('render with existing searchTerm', () => {
    beforeEach(() => {
      props = {
        searchTerm: 'testTerm',
        loadPreviousSearch: jest.fn(),
      };
      subject = shallow(<Breadcrumb {...props} />);
    });

    it('renders Link with correct path', () => {
      expect(subject.find('a').props()).toMatchObject({
        onClick: props.loadPreviousSearch,
      });
    });

    it('renders Link with correct text', () => {
      expect(subject.find('a').find('span').text()).toEqual('Search Results');
    });
  });

  describe('render with existing searchTerm and prop overrides', () => {
    beforeEach(() => {
      props = {
        path: 'testPath',
        text: 'testText',
        searchTerm: 'testTerm',
        loadPreviousSearch: jest.fn(),
      };
      subject = shallow(<Breadcrumb {...props} />);
    });

    it('renders Link with correct path', () => {
      expect(subject.find(Link).props()).toMatchObject({
        to: 'testPath',
      });
    });

    it('renders Link with correct text', () => {
      expect(subject.find(Link).find('span').text()).toEqual('testText');
    });
  });

  describe('mapStateToProps', () => {
    let result;
    beforeAll(() => {
      result = mapStateToProps(globalState);
    });

    it('sets searchTerm on the props', () => {
      expect(result.searchTerm).toEqual(globalState.search.search_term);
    });
  });

  describe('mapDispatchToProps', () => {
    let dispatch;
    let result;
    beforeAll(() => {
      dispatch = jest.fn(() => Promise.resolve());
      result = mapDispatchToProps(dispatch);
    });

    it('sets loadPreviousSearch on the props', () => {
      expect(result.loadPreviousSearch).toBeInstanceOf(Function);
    });
  });
});
