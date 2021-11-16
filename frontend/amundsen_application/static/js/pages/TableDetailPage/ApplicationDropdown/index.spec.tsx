// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { mount } from 'enzyme';

import ApplicationDropdown, { ApplicationDropdownProps } from '.';

const mockAirflowProducingTableApp = {
  application_url: 'http://app_url',
  description: 'description',
  id: 'dag/task1',
  name: 'Airflow',
  kind: 'producing',
};

const mockAirflowConsumingTableApp = {
  application_url: 'http://app_url',
  description: 'description',
  id: 'dag/task2',
  name: 'Airflow',
  kind: 'consuming',
};

const mockDatabricksProducingTableApp = {
  application_url: 'http://app_url',
  description: 'description',
  id: 'dag/task1',
  name: 'Databricks',
  kind: 'producing',
};

const mockDatabricksConsumingTableApp = {
  application_url: 'http://app_url',
  description: 'description',
  id: 'dag/task2',
  name: 'Databricks',
  kind: 'consuming',
};

const mockGenericProducingTableApp = {
  application_url: 'http://app_url',
  description: 'description',
  id: 'id1',
  name: 'Generic Application',
  kind: 'producing',
};

const mockGenericConsumingTableApp = {
  application_url: 'http://app_url',
  description: 'description',
  id: 'id2',
  name: 'Generic Application',
  kind: 'consuming',
};

const setup = (propOverrides?: Partial<ApplicationDropdownProps>) => {
  const props = {
    tableApps: [],
    ...propOverrides,
  };
  const wrapper = mount<typeof ApplicationDropdown>(
    <ApplicationDropdown {...props} />
  );

  return { props, wrapper };
};

describe('ApplicationDropdown', () => {
  describe('render', () => {
    it('renders without issues', () => {
      expect(() => {
        setup();
      }).not.toThrow();
    });

    describe('when no options are passed', () => {
      it('does not render the component', () => {
        const { wrapper } = setup();
        const expected = 0;
        const actual = wrapper.find('.application-dropdown').length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when one option is passed', () => {
      it('renders a Dropdown component', () => {
        const { wrapper } = setup({
          tableApps: [mockAirflowProducingTableApp],
        });
        const expected = 1;
        const actual = wrapper.find(Dropdown).length;

        expect(actual).toEqual(expected);
      });

      it('renders a MenuItem component', () => {
        const { wrapper } = setup({
          tableApps: [mockAirflowProducingTableApp],
        });
        const expected = 1;
        const actual = wrapper.find(MenuItem).length;

        expect(actual).toEqual(expected);
      });

      it('renders one Airflow item', () => {
        const { wrapper } = setup({
          tableApps: [mockAirflowProducingTableApp],
        });
        const expected = 2;
        const actual = wrapper.find(
          '.application-dropdown .application-dropdown-menu-item-row'
        ).length;

        expect(actual).toEqual(expected);
      });

      it('renders one Databricks item', () => {
        const { wrapper } = setup({
          tableApps: [mockDatabricksProducingTableApp],
        });
        const expected = 1;
        const actual = wrapper.find(
          '.application-dropdown .application-dropdown-menu-item-row'
        ).length;

        expect(actual).toEqual(expected);
      });

      it('renders one generic app item', () => {
        const { wrapper } = setup({
          tableApps: [mockGenericProducingTableApp],
        });
        const expected = 1;
        const actual = wrapper.find(
          '.application-dropdown .application-dropdown-menu-item-row'
        ).length;

        expect(actual).toEqual(expected);
      });
    });

    describe('when two options are passed', () => {
      it('renders a Dropdown component', () => {
        const { wrapper } = setup({
          tableApps: [
            mockAirflowProducingTableApp,
            mockAirflowConsumingTableApp,
          ],
        });
        const expected = 1;
        const actual = wrapper.find(Dropdown).length;

        expect(actual).toEqual(expected);
      });

      it('renders two MenuItem components and a MenuItem divider between kinds', () => {
        const { wrapper } = setup({
          tableApps: [
            mockAirflowProducingTableApp,
            mockAirflowConsumingTableApp,
          ],
        });
        const expected = 3;
        const actual = wrapper.find(MenuItem).length;

        expect(actual).toEqual(expected);
      });

      it('renders two Airflow items', () => {
        const { wrapper } = setup({
          tableApps: [
            mockAirflowProducingTableApp,
            mockAirflowConsumingTableApp,
          ],
        });
        const expected = 4;
        const actual = wrapper.find(
          '.application-dropdown .application-dropdown-menu-item-row'
        ).length;

        expect(actual).toEqual(expected);
      });

      it('renders two Databricks items', () => {
        const { wrapper } = setup({
          tableApps: [
            mockDatabricksProducingTableApp,
            mockDatabricksConsumingTableApp,
          ],
        });
        const expected = 2;
        const actual = wrapper.find(
          '.application-dropdown .application-dropdown-menu-item-row'
        ).length;

        expect(actual).toEqual(expected);
      });

      it('renders two generic app items', () => {
        const { wrapper } = setup({
          tableApps: [
            mockGenericProducingTableApp,
            mockGenericConsumingTableApp,
          ],
        });
        const expected = 2;
        const actual = wrapper.find(
          '.application-dropdown .application-dropdown-menu-item-row'
        ).length;

        expect(actual).toEqual(expected);
      });
    });
  });
});
