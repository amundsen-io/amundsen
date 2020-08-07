import * as React from 'react';

import { mount } from 'enzyme';

import globalState from 'fixtures/globalState';
import AvatarLabel from 'components/common/AvatarLabel';

import {
  OwnerEditor,
  OwnerEditorProps,
  mapStateToProps,
  mapDispatchToProps,
} from '.';
import * as Constants from './constants';

describe('OwnerEditor', () => {
  const setup = (propOverrides?: Partial<OwnerEditorProps>) => {
    const props: OwnerEditorProps = {
      errorText: null,
      isLoading: false,
      itemProps: {},
      isEditing: null,
      setEditMode: jest.fn(),
      onUpdateList: jest.fn(),
      readOnly: null,
      ...propOverrides,
    };
    const wrapper = mount<OwnerEditor>(<OwnerEditor {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    describe('when no owners', () => {
      it('renders text if readOnly', () => {
        const { wrapper } = setup({ readOnly: true });
        expect(wrapper.find(AvatarLabel).text()).toContain(
          Constants.NO_OWNER_TEXT
        );
      });

      it('renders add button if not readOnly', () => {
        const { wrapper } = setup();
        expect(wrapper.find('.add-item-button').text()).toContain(
          Constants.ADD_OWNER
        );
      });
    });

    it('renders owners if they exist', () => {
      const { wrapper } = setup({
        itemProps: { owner1: {}, owner2: {}, owner3: {} },
      });
      expect(wrapper.find(AvatarLabel).length).toBe(3);
    });

    describe('editing modal', () => {
      it('renders when not readOnly', () => {
        const { wrapper } = setup();
        expect(wrapper.find('.owner-editor-modal').exists()).toBe(true);
      });

      it('does not render when readOnly', () => {
        const { wrapper } = setup({ readOnly: true });
        expect(wrapper.find('.owner-editor-modal').exists()).toBe(false);
      });
    });
  });
});
