import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import { Breadcrumb, BreadcrumbProps } from '../';

describe('Breadcrumb', () => {
  let props: BreadcrumbProps;
  let subject;

  describe('render', () => {
    beforeEach(() => {
      props = {
        path: 'testPath',
        text: 'testText',
        searchTerm: '',
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
      };
      subject = shallow(<Breadcrumb {...props} />);
    });

    it('renders Link with correct path', () => {
      expect(subject.find(Link).props()).toMatchObject({
        to: '/search',
      });
    });

    it('renders Link with correct text', () => {
      expect(subject.find(Link).find('span').text()).toEqual('Search Results');
    });
  });

  describe('render with existing searchTerm and prop overrides', () => {
    beforeEach(() => {
      props = {
        path: 'testPath',
        text: 'testText',
        searchTerm: 'testTerm',
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
});
