// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as ReactMarkdown from 'react-markdown';

import { shallow } from 'enzyme';
import {
  CANCEL_BUTTON_TEXT,
  REFRESH_BUTTON_TEXT,
  REFRESH_MESSAGE,
  UPDATE_BUTTON_TEXT,
} from 'components/EditableText/constants';
import EditableText, { EditableTextProps } from '.';

const setup = (propOverrides?: Partial<EditableTextProps>) => {
  const props = {
    editable: true,
    isEditing: true,
    maxLength: 4000,
    onSubmitValue: jest.fn(),
    getLatestValue: jest.fn(),
    refreshValue: '',
    setEditMode: jest.fn(),
    value: 'currentValue',
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = shallow<EditableText>(<EditableText {...props} />);

  return {
    props,
    wrapper,
  };
};

describe('EditableText', () => {
  describe('componentDidUpdate', () => {
    it('sets isDisabled:true when refresh value does not equal value', () => {
      const { wrapper, props } = setup({
        isEditing: true,
        refreshValue: 'new value',
        value: 'different value',
      });

      wrapper.instance().componentDidUpdate(props);
      const state = wrapper.state();

      expect(state.isDisabled).toBe(true);
    });
  });

  describe('exitEditMode', () => {
    it('updates the state', () => {
      const { wrapper, props } = setup();
      const instance = wrapper.instance();
      const setEditModeSpy = jest.spyOn(props, 'setEditMode');

      setEditModeSpy.mockClear();
      instance.exitEditMode();

      expect(setEditModeSpy).toHaveBeenCalledWith(false);
      expect(wrapper.state()).toMatchObject({
        isDisabled: false,
      });
    });
  });

  describe('render', () => {
    describe('not in edit mode', () => {
      it('renders a ReactMarkdown component', () => {
        const { wrapper } = setup({
          isEditing: false,
          value: '',
        });
        const markdown = wrapper.find(ReactMarkdown);

        expect(markdown.exists()).toBe(true);
      });

      it('renders an edit link if it is editable and the text is empty', () => {
        const { wrapper } = setup({
          isEditing: false,
          value: '',
        });
        const editLink = wrapper.find('.edit-link');

        expect(editLink.exists()).toBe(true);
      });

      it('does not render an edit link if it is not editable', () => {
        const { wrapper } = setup({ editable: false });
        const editLink = wrapper.find('.edit-link');

        expect(editLink.exists()).toBe(false);
      });
    });

    describe('in edit mode', () => {
      it('renders a textarea ', () => {
        const { wrapper, props } = setup({
          isEditing: true,
          value: '',
        });
        const textarea = wrapper.find('textarea');

        expect(textarea.exists()).toBe(true);
        expect(textarea.props()).toMatchObject({
          maxLength: props.maxLength,
          defaultValue: wrapper.state().value,
          disabled: wrapper.state().isDisabled,
        });
      });

      it('when disabled, renders the refresh message and button', () => {
        const { wrapper } = setup({
          isEditing: true,
          value: '',
        });

        wrapper.setState({ isDisabled: true });
        const refreshMessage = wrapper.find('.refresh-message');

        expect(refreshMessage.text()).toBe(REFRESH_MESSAGE);

        const refreshButton = wrapper.find('.refresh-button');

        expect(refreshButton.text()).toMatch(REFRESH_BUTTON_TEXT);
      });

      it('when not disabled, renders the update text button', () => {
        const { wrapper } = setup({
          isEditing: true,
          value: '',
        });

        wrapper.setState({ isDisabled: false });
        const updateButton = wrapper.find('.update-button');

        expect(updateButton.text()).toMatch(UPDATE_BUTTON_TEXT);
      });

      it('renders the cancel button', () => {
        const { wrapper } = setup({
          isEditing: true,
          value: '',
        });
        const cancelButton = wrapper.find('.cancel-button');

        expect(cancelButton.text()).toMatch(CANCEL_BUTTON_TEXT);
      });
    });
  });
});
