// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';

import AvatarLabel from 'components/AvatarLabel';
import { ResourceType } from 'interfaces';

import * as ConfigUtils from 'config/config-utils';
import InfoButton from 'components/InfoButton';
import { OwnerEditor, OwnerEditorProps } from '.';

import * as Constants from './constants';

const setup = (propOverrides?: Partial<OwnerEditorProps>) => {
  const props: OwnerEditorProps = {
    errorText: null,
    isLoading: false,
    itemProps: {},
    isEditing: undefined,
    setEditMode: jest.fn(),
    onUpdateList: jest.fn(),
    readOnly: undefined,
    resourceType: ResourceType.table,
    ...propOverrides,
  };
  // eslint-disable-next-line react/jsx-props-no-spreading
  const wrapper = mount<OwnerEditor>(<OwnerEditor {...props} />);

  return {
    props,
    wrapper,
  };
};

describe('OwnerEditor', () => {
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

  describe('renderOwnersList', () => {
    it('renders list of owners when categories not configured', () => {
      const { wrapper } = setup({
        itemProps: { owner1: {}, owner2: {}, owner3: {} },
      });

      expect(wrapper.find(AvatarLabel).length).toBe(3);
      expect(wrapper.find(InfoButton).length).toBe(0); // expect no info buttons when owners not configured
    });

    it('renders owners when categories configured and present on all owners', () => {
      jest.spyOn(ConfigUtils, 'getOwnersSectionConfig').mockReturnValue({
        categories: [
          { label: 'label1', definition: 'label1 definition' },
          { label: 'label2', definition: 'label2 definition' },
        ],
      });

      const { wrapper } = setup({
        itemProps: {
          owner1: { additionalOwnerInfo: { owner_category: 'label1' } },
          owner2: { additionalOwnerInfo: { owner_category: 'label1' } },
          owner3: { additionalOwnerInfo: { owner_category: 'label2' } },
        },
      });

      expect(wrapper.find(AvatarLabel).length).toBe(6); // expect 2 for each owner because InfoButton is rendered
      expect(wrapper.find(InfoButton).length).toBe(2); // expect one for each category
    });

    it('renders owners when categories configured but not present on these owners', () => {
      jest.spyOn(ConfigUtils, 'getOwnersSectionConfig').mockReturnValue({
        categories: [{ label: 'label1', definition: 'label1 definition' }],
      });

      const { wrapper } = setup({
        itemProps: {
          owner1: {},
          owner2: {},
          owner3: {},
        },
      });

      expect(wrapper.find(AvatarLabel).length).toBe(3);
    });

    it('renders owners without errors when some owners have categories and some do not', () => {
      jest.spyOn(ConfigUtils, 'getOwnersSectionConfig').mockReturnValue({
        categories: [{ label: 'label1', definition: 'label1 definition' }],
      });

      const { wrapper } = setup({
        itemProps: {
          owner1: { additionalOwnerInfo: { owner_category: 'label1' } },
          owner2: {},
          owner3: {},
        },
      });

      expect(wrapper.find(AvatarLabel).length).toBe(3);
    });
  });
});
