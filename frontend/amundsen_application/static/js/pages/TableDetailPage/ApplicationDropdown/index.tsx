// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';

import AvatarLabel from 'components/AvatarLabel';
import { TableApp } from 'interfaces';
import { logClick } from 'utils/analytics';
import {
  APPLICATIONS_LABEL,
  AIRFLOW,
  DATABRICKS,
  PRODUCING,
  CONSUMING,
  DAG_LABEL,
  TASK_LABEL,
  NOT_AVAILABLE_VALUE,
} from './constants';
import './styles.scss';

export interface ApplicationDropdownProps {
  tableApps: TableApp[];
}

const getImagePath = (tableAppName) => {
  switch (tableAppName) {
    case AIRFLOW:
      return '/static/images/airflow.jpeg';
    case DATABRICKS:
      return '/static/images/icons/logo-databricks.png';
    default:
      return '/static/images/icons/application.svg';
  }
};

const isAirflowOrDatabricksApp = (appName) =>
  appName.toLowerCase() === AIRFLOW || appName.toLowerCase() === DATABRICKS;

const sortByNameOrId = (a, b) =>
  a.name.localeCompare(b.name) || a.id.localeCompare(b.id);

const hasSameNameAndKind = (app, name, kind) =>
  // Checks if the app matches the given name and kind
  // If its kind is empty, check if the given kind is the default Producing value
  app.name === name &&
  ((app.kind && app.kind === kind) || (!app.kind && kind === PRODUCING));

const getSortedAppKinds = (apps: TableApp[]) => {
  // Sort app kinds by Producing then Consuming if they exist in the list, and then all others following
  // If no kind is specified, default to Producing
  const appKinds: string[] = [
    ...new Set(apps.map((app) => (app.kind ? app.kind : PRODUCING))),
  ];

  const producingKind = appKinds.filter(
    (kind) => kind.toLowerCase() === PRODUCING
  );
  const consumingKind = appKinds.filter(
    (kind) => kind.toLowerCase() === CONSUMING
  );
  const remainingKinds = appKinds.filter(
    (kind) =>
      kind.toLowerCase() !== PRODUCING && kind.toLowerCase() !== CONSUMING
  );

  return [...producingKind, ...consumingKind, ...remainingKinds];
};

const handleClick = (event) => {
  event.stopPropagation();
  logClick(event);
};

const getMenuItem = (app: TableApp) => {
  const isAirflowApp = app.name.toLowerCase() === AIRFLOW;
  const [dagId, ...task] = app.id.split('/');
  const taskId = task.join('/');

  return (
    <OverlayTrigger
      key={app.id}
      trigger={['hover', 'focus']}
      placement="top"
      delayShow={500}
      overlay={<Popover id="popover-trigger-hover-focus">{app.id}</Popover>}
    >
      <MenuItem
        href={app.application_url}
        onClick={handleClick}
        target="_blank"
        rel="noopener noreferrer"
      >
        {isAirflowApp ? (
          <div>
            <div className="application-dropdown-menu-item-row airflow-app">
              <span className="section-title">{DAG_LABEL}</span>
              <span className="menu-item-content">
                {dagId || NOT_AVAILABLE_VALUE}
              </span>
            </div>
            <div className="application-dropdown-menu-item-row airflow-app">
              <span className="section-title">{TASK_LABEL}</span>
              <span className="menu-item-content">
                {taskId || NOT_AVAILABLE_VALUE}
              </span>
            </div>
          </div>
        ) : (
          <div className="application-dropdown-menu-item-row">
            <span className="menu-item-content">{app.id}</span>
          </div>
        )}
      </MenuItem>
    </OverlayTrigger>
  );
};

const ApplicationDropdown: React.FC<ApplicationDropdownProps> = ({
  tableApps,
}: ApplicationDropdownProps) => {
  if (tableApps === null || tableApps.length === 0) return null;

  const image = getImagePath(tableApps[0].name.toLowerCase());

  tableApps.sort(sortByNameOrId);
  const appNames: string[] = [...new Set(tableApps.map(({ name }) => name))];

  // Group the applications in the dropdown by name then kind
  let menuItems: React.ReactNode[] = [];
  appNames.forEach((name, nameIdx) => {
    const appKinds = getSortedAppKinds(
      tableApps.filter((app) => app.name === name)
    );
    appKinds.forEach((kind, kindIdx) => {
      const sectionTitle = isAirflowOrDatabricksApp(tableApps[0].name)
        ? kind
        : name + ' - ' + kind;
      menuItems = [
        ...menuItems,
        <h5 key={sectionTitle} className="application-dropdown-menu-title">
          {sectionTitle}
        </h5>,
      ];
      menuItems = [
        ...menuItems,
        ...tableApps
          .filter((app) => hasSameNameAndKind(app, name, kind))
          .map((app) => getMenuItem(app)),
      ];
      if (kindIdx + 1 < appKinds.length || nameIdx + 1 < appNames.length) {
        menuItems = [...menuItems, <MenuItem divider />];
      }
    });
  });

  const avatarLabel = isAirflowOrDatabricksApp(tableApps[0].name)
    ? tableApps[0].name
    : APPLICATIONS_LABEL;
  return (
    <Dropdown
      className="header-link application-dropdown"
      id="application-dropdown"
      pullRight
    >
      <Dropdown.Toggle className="application-dropdown-button">
        <AvatarLabel
          label={avatarLabel}
          src={image}
          round={isAirflowOrDatabricksApp(tableApps[0].name)}
        />
      </Dropdown.Toggle>
      <Dropdown.Menu className="application-dropdown-menu">
        {menuItems}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default ApplicationDropdown;
