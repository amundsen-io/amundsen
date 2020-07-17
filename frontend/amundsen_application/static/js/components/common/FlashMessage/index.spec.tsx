// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { shallow } from 'enzyme';

import FlashMessage, { FlashMessageProps } from '.';

describe('FlashMessage', () => {
  const setup = (propOverrides?: Partial<FlashMessageProps>) => {
    const props: FlashMessageProps = {
      iconClass: null,
      message: 'Test',
      onClose: jest.fn(),
      ...propOverrides,
    };
    const wrapper = shallow(<FlashMessage {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    let props: FlashMessageProps;
    let wrapper;
    beforeAll(() => {
      const setupResult = setup();
      props = setupResult.props;
      wrapper = setupResult.wrapper;
    });

    describe('iconClass logic', () => {
      it('if no iconClass, does not render img', () => {
        expect(wrapper.find('img').exists()).toBe(false);
      });

      it('if iconClass, renders img with correct className', () => {
        const testClass = 'icon-mail';
        const { wrapper } = setup({ iconClass: testClass });
        expect(wrapper.find('img').props()).toMatchObject({
          className: `icon ${testClass}`,
        });
      });
    });

    it('renders correct message text', () => {
      expect(wrapper.find('div.message').text()).toBe(props.message);
    });

    it('renders correct button', () => {
      expect(wrapper.find('button.btn.btn-close').props().onClick).toBe(
        props.onClose
      );
    });
  });
});
