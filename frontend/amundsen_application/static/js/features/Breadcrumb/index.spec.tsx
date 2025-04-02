// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { shallow } from 'enzyme';

import { Link } from 'react-router-dom';
import { Breadcrumb, BreadcrumbProps, mapDispatchToProps } from '.';

const setup = (propOverrides?: Partial<BreadcrumbProps>) => {
  const props: BreadcrumbProps = {
    loadPreviousSearch: jest.fn(),
    ...propOverrides,
  };
  const wrapper = shallow(<Breadcrumb {...props} />);

  return { props, wrapper };
};

describe('Breadcrumb', () => {
  describe('render', () => {
    let props: BreadcrumbProps;
    let wrapper;

    describe('when given path & text', () => {
      beforeAll(() => {
        ({ wrapper, props } = setup({ path: 'testPath', text: 'testText' }));
      });

      it('renders Link with given path', () => {
        expect(wrapper.find(Link).props()).toMatchObject({
          to: props.path,
        });
      });

      it('renders Link with given text', () => {
        expect(wrapper.find(Link).find('span').text()).toEqual(props.text);
      });

      it('renders left icon by default', () => {
        expect(wrapper.find(Link).find('img').props().className).toEqual(
          'icon icon-left'
        );
      });

      it('renders left icon when props.direction = "left"', () => {
        ({ wrapper } = setup({
          path: 'testPath',
          text: 'testText',
          direction: 'left',
        }));

        expect(wrapper.find(Link).find('img').props().className).toEqual(
          'icon icon-left'
        );
      });

      it('renders right icon when props.direction = "right"', () => {
        ({ wrapper } = setup({
          path: 'testPath',
          text: 'testText',
          direction: 'right',
        }));

        expect(wrapper.find(Link).find('img').props().className).toEqual(
          'icon icon-right'
        );
      });
    });

    describe('when not given path or text', () => {
      beforeAll(() => {
        ({ wrapper, props } = setup());
      });

      it('renders left icon by default', () => {
        expect(wrapper.find('a').find('img').props().className).toEqual(
          'icon icon-left'
        );
      });

      it('renders left icon when props.direction = "left"', () => {
        ({ wrapper } = setup({ direction: 'left' }));

        expect(wrapper.find('a').find('img').props().className).toEqual(
          'icon icon-left'
        );
      });

      it('renders right icon when props.direction = "right"', () => {
        ({ wrapper } = setup({ direction: 'right' }));

        expect(wrapper.find('a').find('img').props().className).toEqual(
          'icon icon-right'
        );
      });
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
