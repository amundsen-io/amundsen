// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';

import AvatarLabel from 'components/AvatarLabel';

import { ResourceType } from 'interfaces';
import { getOwnersSectionConfig } from 'config/config-utils';

import { OwnerEditor, OwnerEditorProps } from '.';
import { OwnerCategory } from 'interfaces/OwnerCategory';
// import { renderOwnersSection } from './OwnerEditor';
import { OwnersSectionConfig } from 'config/config-types';

import * as Constants from './constants';

import * as ConfigUtils from 'config/config-utils';

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
    });

    // getOwnersSectionConfig.mockReturnValue({ section: 'mocked config' });

    it('renders owners grouped by category when categories configured', () => {
      const { wrapper } = setup({
        itemProps: {
          owner1: { additionalOwnerInfo: { owner_category: 'label1' } },
          // owner2: {},
          // owner3: {},
        },
      });

      jest.spyOn(ConfigUtils, 'getOwnersSectionConfig').mockReturnValue({
        categories: [{ label: 'label1', definition: 'label1 definition' }],
      });

      console.log(wrapper.debug());

      expect(wrapper.find(AvatarLabel).length).toBe(1);
      // expect(wrapper.find(AvatarLabel).additionalOwnerInfo).toContain('label1');
      // expect(wrapper.find('.owner-category-label').text()).toContain('label1');
    });
  });

  // describe('renderOwnersList', () => {
  //   const { wrapper } = setup({
  //     itemProps: { owner1: {}, owner2: {}, owner3: {} },
  //   });

  //   jest.spyOn(ConfigUtils, 'getOwnersSectionConfig').mockReturnValue({
  //     categories: [{ label: 'label1', definition: 'label1 definition' }],
  //   });
  // });

  // describe('renderOwnersSection', () => {
  //   it('renders section for each category', () => {
  //     const section: OwnerCategory = {
  //       label: 'label1',
  //       definition: 'label1 definition',
  //     };
  //     const result = renderOwnersSection(section);

  //     expect(result.length).toBe(1);
  //   });
  // });
});
