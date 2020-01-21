import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import { Breadcrumb, BreadcrumbProps, mapDispatchToProps } from '../';

describe('Breadcrumb', () => {
  let props: BreadcrumbProps;
  let subject;

  describe('render', () => {
    beforeEach(() => {
      props = {
        path: 'testPath',
        text: 'testText',
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
        loadPreviousSearch: jest.fn(),
      };
      subject = shallow(<Breadcrumb {...props} />);
    });

    it('renders Link with correct path', () => {
      expect(subject.find('a').props()).toMatchObject({
        onClick: props.loadPreviousSearch,
      });
    });
  });

  describe('render with existing searchTerm and prop overrides', () => {
    beforeEach(() => {
      props = {
        path: 'testPath',
        text: 'testText',
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
