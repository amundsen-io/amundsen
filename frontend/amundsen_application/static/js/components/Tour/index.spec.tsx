// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';
import { act } from 'react-dom/test-utils';
import Joyride from 'react-joyride';

import { Tour, TourProps } from '.';

jest.mock('@rehooks/local-storage', () => ({
  useLocalStorage() {
    return [false];
  },
  writeStorage() {},
}));

const setup = (propOverrides?: Partial<TourProps>) => {
  const props = {
    run: true,
    steps: [
      {
        target: 'body',
        title: 'Test Title',
        content: 'Test Content',
      },
    ],
    ...propOverrides,
  };
  const wrapper = mount<TourProps>(<Tour {...props} />);

  return { props, wrapper };
};

describe('Tour', () => {
  (global as any).document.createRange = () => ({
    setStart: () => {},
    setEnd: () => {},
    commonAncestorContainer: {
      nodeName: 'BODY',
      ownerDocument: document,
    },
  });

  describe('render', () => {
    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    it('renders the Joyride component', () => {
      const { wrapper } = setup();
      const expected = 1;
      const actual = wrapper.find(Joyride).length;

      expect(actual).toEqual(expected);
    });

    describe('prop drilling', () => {
      it('passes the run prop', () => {
        const { wrapper } = setup();
        const expected = true;
        const actual = wrapper.find(Joyride).prop('run');

        expect(actual).toEqual(expected);
      });

      it('passes the steps prop', () => {
        const { wrapper, props } = setup();
        const expected = props.steps;
        const actual = wrapper.find(Joyride).prop('steps');

        expect(actual).toEqual(expected);
      });
    });

    describe('when overriding configuration', () => {
      it('passes the new configuration', () => {
        const { wrapper } = setup({
          configurationOverrides: { continuous: false },
        });
        const expected = false;
        const actual = wrapper.find(Joyride).prop('continuous');

        expect(actual).toEqual(expected);
      });
    });

    describe('when tour is NOT set to run', () => {
      it('should keep the steps hidden', () => {
        const { wrapper } = setup({ run: false });
        const expected = 0;
        const actual = wrapper.find('.react-joyride').children().length;

        expect(actual).toEqual(expected);
      });
    });
  });

  describe('lifetime', () => {
    describe('when finishing the tour', () => {
      it('should call the onTourEnd handler', () => {
        const onTourEndSpy = jest.fn();
        const expected = 2; // Not sure why joyrides triggers the callback twice for each state change
        const { wrapper } = setup({ onTourEnd: onTourEndSpy });

        act(() => {
          wrapper.find('button[aria-label="Done"]').simulate('click');
        });
        const actual = onTourEndSpy.mock.calls.length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when tour is set to trigger on first view', () => {
      beforeEach(() => {
        jest.useFakeTimers();
      });

      afterEach(() => {
        jest.useRealTimers();
      });

      it('should show up after the delay', () => {
        const { wrapper } = setup({ run: false, triggersOnFirstView: true });
        const expected = true;

        act(() => {
          jest.runAllTimers();
        });

        wrapper.update();
        const actual = wrapper.find('.react-joyride').children().length > 0;

        expect(actual).toEqual(expected);
      });
    });
  });
});
