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

    it('renders button with correct text within the Link', () => {
      expect(subject.find(Link).find('button').text()).toEqual(props.text);
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
        to: '/search?searchTerm=testTerm&selectedTab=table&pageIndex=0',
      });
    });

    it('renders button with correct text within the Link', () => {
      expect(subject.find(Link).find('button').text()).toEqual('Search Results');
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

    it('renders button with correct text within the Link', () => {
      expect(subject.find(Link).find('button').text()).toEqual('testText');
    });
  });
});
