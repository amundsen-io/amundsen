// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import ColumnDescEditableText from 'components/TableDetail/ColumnDescEditableText';
import {
  ColumnListItem,
  ColumnListItemProps,
  mapDispatchToProps,
} from 'components/TableDetail/ColumnListItem';
import EditableSection from 'components/common/EditableSection';
import ColumnStats from 'components/TableDetail/ColumnStats';
import AppConfig from 'config/config';
import * as UtilMethods from 'ducks/utilMethods';
import { RequestMetadataType } from 'interfaces/Notifications';

const logClickSpy = jest.spyOn(UtilMethods, 'logClick');
logClickSpy.mockImplementation(() => null);

describe('ColumnListItem', () => {
  const setup = (propOverrides?: Partial<ColumnListItemProps>) => {
    const props = {
      data: {
        name: 'test_column_name',
        description: 'This is a test description of this table',
        is_editable: true,
        col_type: 'varchar(32)',
        stats: [
          {
            end_epoch: 1571616000,
            start_epoch: 1571616000,
            stat_type: 'count',
            stat_val: '12345',
          },
        ],
      },
      index: 0,
      openRequestDescriptionDialog: jest.fn(),
      editText: 'Click to edit discription in source',
      editUrl: 'source/test_column_name',
      ...propOverrides,
    };

    const wrapper = shallow<ColumnListItem>(<ColumnListItem {...props} />);
    return { wrapper, props };
  };

  const { wrapper, props } = setup();
  const instance = wrapper.instance();
  const setStateSpy = jest.spyOn(instance, 'setState');

  describe('toggleExpand', () => {
    it('calls the logClick when isExpanded is false', () => {
      instance.setState({ isExpanded: false });
      logClickSpy.mockClear();
      instance.toggleExpand(null);
      expect(logClickSpy).toHaveBeenCalled();
    });

    it('does not calls the logClick when isExpanded is true', () => {
      instance.setState({ isExpanded: true });
      logClickSpy.mockClear();
      instance.toggleExpand(null);
      expect(logClickSpy).not.toHaveBeenCalled();
    });

    it('turns expanded state to the opposite state', () => {
      setStateSpy.mockClear();
      const prevState = instance.state;
      instance.toggleExpand(null);
      expect(setStateSpy).toHaveBeenCalled();
    });
  });

  describe('openRequest', () => {
    it('calls openRequestDescriptionDialog', () => {
      const openRequestDescriptionDialogSpy = jest.spyOn(
        props,
        'openRequestDescriptionDialog'
      );
      instance.openRequest();
      expect(openRequestDescriptionDialogSpy).toHaveBeenCalledWith(
        RequestMetadataType.COLUMN_DESCRIPTION,
        props.data.name
      );
    });
  });

  describe('render', () => {
    it('renders a list-group-item with toggle expand attached', () => {
      const listGroupItem = wrapper.find('.list-group-item');
      expect(listGroupItem.props()).toMatchObject({
        onClick: instance.toggleExpand,
      });
    });

    it('renders the column name correctly', () => {
      const columnName = wrapper.find('.column-name');
      expect(columnName.text()).toBe(props.data.name);
    });

    it('renders the column description when not expanded', () => {
      instance.setState({ isExpanded: false });
      const columnDesc = wrapper.find('.column-desc');
      expect(columnDesc.text()).toBe(props.data.description);
    });

    it('renders the correct resource type', () => {
      const resourceType = wrapper.find('.resource-type');
      expect(resourceType.text()).toBe(props.data.col_type.toLowerCase());
    });

    it('renders the dropdown when notifications is enabled', () => {
      AppConfig.mailClientFeatures.notificationsEnabled = true;
      const { wrapper, props } = setup();
      expect(wrapper.find('.column-dropdown').exists()).toBe(true);
    });

    it('does not render the dropdown when notifications is disabled', () => {
      AppConfig.mailClientFeatures.notificationsEnabled = false;
      const { wrapper, props } = setup();
      expect(wrapper.find('.column-dropdown').exists()).toBe(false);
    });

    describe('when expanded', () => {
      it('renders column stats and editable text', () => {
        instance.setState({ isExpanded: true });
        const newWrapper = shallow(instance.render());
        expect(newWrapper.find('.expanded-content').exists()).toBe(true);
        expect(newWrapper.find(EditableSection).exists()).toBe(true);
        expect(newWrapper.find(ColumnDescEditableText).exists()).toBe(true);
        expect(newWrapper.find(ColumnStats).exists()).toBe(true);
      });

      it('renders EditableSection with non-empty description, edit text and url', () => {
        instance.setState({ isExpanded: true });
        const newWrapper = shallow(instance.render());
        const editableSection = newWrapper.find(EditableSection);
        expect(editableSection.props()).toMatchObject({
          title: 'Description',
          readOnly: !props.data.is_editable,
          editText: props.editText,
          editUrl: props.editUrl,
        });
      });

      it('renders EditableSection with non-empty description, empty edit text and url', () => {
        const { props, wrapper } = setup({
          editText: '',
          editUrl: '',
        });
        const instance = wrapper.instance();
        instance.setState({ isExpanded: true });
        const newWrapper = shallow(instance.render());
        expect(newWrapper.find(EditableSection).exists()).toBe(true);
        const editableSection = newWrapper.find(EditableSection);
        expect(editableSection.props()).toMatchObject({
          title: 'Description',
          readOnly: !props.data.is_editable,
          editText: props.editText,
          editUrl: props.editUrl,
        });
      });

      describe('when empty description', () => {
        it('renders EditableSection with empty edit text and url for editable column description', () => {
          const { props, wrapper } = setup({
            data: {
              name: 'test_column_name',
              description: '',
              is_editable: true,
              col_type: 'varchar(32)',
              stats: [
                {
                  end_epoch: 1571616000,
                  start_epoch: 1571616000,
                  stat_type: 'count',
                  stat_val: '12345',
                },
              ],
            },
            editText: '',
            editUrl: '',
          });
          const instance = wrapper.instance();
          instance.setState({ isExpanded: true });
          const newWrapper = shallow(instance.render());
          expect(newWrapper.find(EditableSection).exists()).toBe(true);
          const editableSection = newWrapper.find(EditableSection);
          expect(editableSection.props()).toMatchObject({
            title: 'Description',
            readOnly: !props.data.is_editable,
            editText: props.editText,
            editUrl: props.editUrl,
          });
        });

        it('does not render EditableSection with empty edit text and url for non-editable column description', () => {
          const { wrapper } = setup({
            data: {
              name: 'test_column_name',
              description: '',
              is_editable: false,
              col_type: 'varchar(32)',
              stats: [
                {
                  end_epoch: 1571616000,
                  start_epoch: 1571616000,
                  stat_type: 'count',
                  stat_val: '12345',
                },
              ],
            },
            editText: '',
            editUrl: '',
          });
          const instance = wrapper.instance();
          instance.setState({ isExpanded: true });
          const newWrapper = shallow(instance.render());
          expect(newWrapper.find(EditableSection).exists()).toBe(false);
        });

        it('renders EditableSection with non-empty edit text and url for non-editable column description', () => {
          const { props, wrapper } = setup({
            data: {
              name: 'test_column_name',
              description: '',
              is_editable: false,
              col_type: 'varchar(32)',
              stats: [
                {
                  end_epoch: 1571616000,
                  start_epoch: 1571616000,
                  stat_type: 'count',
                  stat_val: '12345',
                },
              ],
            },
            editText: 'Click to edit description in source',
            editUrl: 'source/test_column_name',
          });
          const instance = wrapper.instance();
          instance.setState({ isExpanded: true });
          const newWrapper = shallow(instance.render());
          expect(newWrapper.find(EditableSection).exists()).toBe(true);
          const editableSection = newWrapper.find(EditableSection);
          expect(editableSection.props()).toMatchObject({
            title: 'Description',
            readOnly: !props.data.is_editable,
            editText: props.editText,
            editUrl: props.editUrl,
          });
        });
      });
    });
    describe('when not expanded', () => {
      let newWrapper;
      beforeAll(() => {
        instance.setState({ isExpanded: false });
        newWrapper = shallow(instance.render());
      });

      it('does not render column stats', () => {
        expect(newWrapper.find('.expanded-content').exists()).toBe(false);
        expect(newWrapper.find(ColumnDescEditableText).exists()).toBe(false);
        expect(newWrapper.find(ColumnStats).exists()).toBe(false);
      });

      it('has appropriate css for column details', () => {
        expect(newWrapper.find('.column-details').hasClass('my-auto')).toBe(
          true
        );
      });
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

  it('sets openRequestDescriptionDialog on the props', () => {
    expect(result.openRequestDescriptionDialog).toBeInstanceOf(Function);
  });
});
