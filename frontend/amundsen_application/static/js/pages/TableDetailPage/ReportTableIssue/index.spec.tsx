// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { shallow } from 'enzyme';

import globalState from 'fixtures/globalState';
import { NotificationType } from 'interfaces';
import { ReportTableIssue, ReportTableIssueProps, mapDispatchToProps } from '.';

const globalAny: any = global;

let mockGetIssueDescriptionTemplate = 'This is a description template';
let mockIssueTrackingProjectSelectionEnabled = true;
jest.mock('config/config-utils', () => {
  const configUtilsModule = jest.requireActual('config/config-utils');
  return {
    ...configUtilsModule,
    getIssueDescriptionTemplate: () => mockGetIssueDescriptionTemplate,
    issueTrackingProjectSelectionEnabled: () =>
      mockIssueTrackingProjectSelectionEnabled,
  };
});

const mockFormData = {
  key: 'val1',
  title: 'title',
  description: 'description',
  owner_ids: ['owner@email'],
  frequent_user_ids: ['frequent@email'],
  priority_level: 'priority level',
  project_key: 'project key',
  resource_name: 'resource name',
  resource_path: 'path',
  owners: 'test@test.com',
  get: jest.fn(),
};
mockFormData.get.mockImplementation((val) => mockFormData[val]);
function formDataMock() {
  this.append = jest.fn();
  return mockFormData;
}
globalAny.FormData = formDataMock;

const mockCreateIssuePayload = {
  key: 'key',
  title: 'title',
  description: 'description',
  owner_ids: ['owner@email'],
  frequent_user_ids: ['frequent@email'],
  priority_level: 'P2',
  project_key: 'project key',
  resource_path: '/table_detail/cluster/database/schema/table_name',
};

const mockNotificationPayload = {
  notificationType: NotificationType.DATA_ISSUE_REPORTED,
  options: {
    resource_name: 'schema.table_name',
    resource_path: '/table_detail/cluster/database/schema/table_name',
  },
  recipients: ['owner@email'],
  sender: 'user@email',
};

describe('ReportTableIssue', () => {
  const setStateSpy = jest.spyOn(ReportTableIssue.prototype, 'setState');
  const setup = (propOverrides?: Partial<ReportTableIssueProps>) => {
    const props: ReportTableIssueProps = {
      createIssue: jest.fn(),
      tableKey: 'key',
      tableName: 'name',
      tableOwners: ['owner@email'],
      frequentUsers: ['frequent@email'],
      tableMetadata: {
        ...globalState.tableMetadata.tableData,
        schema: 'schema',
        name: 'table_name',
        cluster: 'cluster',
        database: 'database',
      },
      userEmail: 'user@email',
      ...propOverrides,
    };
    const wrapper = shallow<ReportTableIssue>(<ReportTableIssue {...props} />);
    return { props, wrapper };
  };

  describe('render', () => {
    it('Renders loading spinner if not ready', () => {
      const { wrapper } = setup();

      expect(wrapper.find('.loading-spinner')).toBeTruthy();
    });

    it('Renders modal if open', () => {
      const { wrapper } = setup();

      wrapper.setState({ isOpen: true });

      expect(wrapper.find('.report-table-issue-modal')).toBeTruthy();
    });

    it('Renders description template', () => {
      mockGetIssueDescriptionTemplate = 'This is a description template';
      const { wrapper } = setup();
      wrapper.setState({ isOpen: true });

      expect(wrapper.find('textarea').props().defaultValue).toEqual(
        mockGetIssueDescriptionTemplate
      );
    });

    it('Renders empty description template', () => {
      mockGetIssueDescriptionTemplate = '';
      const { wrapper } = setup();
      wrapper.setState({ isOpen: true });

      expect(wrapper.find('textarea').props().defaultValue).toEqual(
        mockGetIssueDescriptionTemplate
      );
    });

    it('Does not render project selection field', () => {
      mockIssueTrackingProjectSelectionEnabled = false;
      const { wrapper } = setup();
      wrapper.setState({ isOpen: true });

      // There should only be one input for issue title
      expect(wrapper.find('input')).toHaveLength(1);
    });

    it('Renders project selection field', () => {
      mockIssueTrackingProjectSelectionEnabled = true;
      const { wrapper } = setup();
      wrapper.setState({ isOpen: true });

      // There should be two inputs, one for issue title and one for project selection
      expect(wrapper.find('input')).toHaveLength(2);
    });

    describe('toggle', () => {
      it('calls setState with negation of state.isOpen', () => {
        setStateSpy.mockClear();
        const { wrapper } = setup();
        const previsOpenState = wrapper.state().isOpen;

        wrapper.instance().toggle({
          currentTarget: { id: 'id', nodeName: 'button' },
        });

        expect(setStateSpy).toHaveBeenCalledWith({ isOpen: !previsOpenState });
      });
    });

    describe('submitForm', () => {
      it('calls createIssue with mocked form data', () => {
        const { props, wrapper } = setup();

        // @ts-ignore: mocked events throw type errors
        wrapper.instance().submitForm({
          preventDefault: jest.fn(),
          currentTarget: { id: 'id', nodeName: 'button' },
        });

        expect(props.createIssue).toHaveBeenCalledWith(
          mockCreateIssuePayload,
          mockNotificationPayload
        );
        expect(wrapper.state().isOpen).toBe(false);
      });

      it('calls sets isOpen to false', () => {
        const { wrapper } = setup();

        // @ts-ignore: mocked events throw type errors
        wrapper.instance().submitForm({
          preventDefault: jest.fn(),
          currentTarget: { id: 'id', nodeName: 'button' },
        });

        expect(wrapper.state().isOpen).toBe(false);
      });
    });

    describe('mapDispatchToProps', () => {
      let dispatch;
      let props;

      beforeAll(() => {
        dispatch = jest.fn(() => Promise.resolve());
        props = mapDispatchToProps(dispatch);
      });

      it('sets getIssues on the props', () => {
        expect(props.createIssue).toBeInstanceOf(Function);
      });
    });
  });
});
