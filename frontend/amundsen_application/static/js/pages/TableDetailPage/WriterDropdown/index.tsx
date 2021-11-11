// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';

import AvatarLabel from 'components/AvatarLabel';
import { TableWriter } from 'interfaces';
import { logClick } from 'utils/analytics';
import {
  APPLICATIONS_LABEL,
  AIRFLOW,
  DATABRICKS,
  PRODUCING,
  CONSUMING,
  DAG_LABEL,
  TASK_LABEL,
  NONE_VALUE,
} from './constants';
import './styles.scss';

export interface WriterDropdownProps {
  tableApps: TableWriter[];
}

const isAirflowOrDatabricksApp = (appName) =>
  appName.toLowerCase() === AIRFLOW || appName.toLowerCase() === DATABRICKS;

const getSortedAppKinds = (apps: TableWriter[]) => {
  const appKinds: string[] = [
    ...new Set(apps.map((app) => (app.kind ? app.kind : PRODUCING))),
  ];

  const producingKind = appKinds.filter(
    (kind) => kind.toLowerCase() === PRODUCING
  );
  const consumingKind = appKinds.filter(
    (kind) => kind.toLowerCase() === CONSUMING
  );

  const sortedKinds: string[] = [];
  sortedKinds.push(...producingKind, ...consumingKind);
  sortedKinds.push(
    ...appKinds.filter(
      (kind) =>
        kind.toLowerCase() !== PRODUCING && kind.toLowerCase() !== CONSUMING
    )
  );
  return sortedKinds;
};

const getMenuItem = (app: TableWriter, menuItemClassName) => {
  if (app.name.toLowerCase() === AIRFLOW) {
    const [dagId, ...task] = app.id.split('/');
    const taskId = task.join('/');
    return (
      <MenuItem
        className={menuItemClassName}
        href={app.application_url}
        onClick={logClick}
        target="_blank"
      >
        <div className="writer-dropdown-menu-item-row airflow-app">
          <span className="section-title">{DAG_LABEL}</span>
          <span className="menu-item-content">{dagId || NONE_VALUE}</span>
        </div>
        <div className="writer-dropdown-menu-item-row airflow-app">
          <span className="section-title">{TASK_LABEL}</span>
          <span className="menu-item-content">{taskId || NONE_VALUE}</span>
        </div>
      </MenuItem>
    );
  }
  return (
    <MenuItem
      className={menuItemClassName}
      href={app.application_url}
      onClick={logClick}
      target="_blank"
    >
      <div className="writer-dropdown-menu-item-row">
        <span className="menu-item-content">
          {app.id ? app.id : NONE_VALUE}
        </span>
      </div>
    </MenuItem>
  );
};

const WriterDropdown: React.FC<WriterDropdownProps> = ({
  tableApps,
}: WriterDropdownProps) => {
  const tableAppName = tableApps[0].name.toLowerCase();

  let image = '';
  switch (tableAppName) {
    case AIRFLOW:
      image = '/static/images/airflow.jpeg';
      break;
    case DATABRICKS:
      image = '/static/images/icons/logo-databricks.png';
      break;
    default:
      image = '/static/images/icons/Application.svg';
  }

  tableApps.sort(
    (a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id)
  );
  const appNames: string[] = [...new Set(tableApps.map((app) => app.name))];

  const menuItems: JSX.Element[] = [];
  let appsDefinedCount = 0;
  appNames.forEach((name, nameIdx) => {
    const appKinds = getSortedAppKinds(
      tableApps.filter((app) => app.name === name)
    );
    appKinds.forEach((kind, kindIdx) => {
      const sectionTitle = isAirflowOrDatabricksApp(tableApps[0].name)
        ? kind
        : name + ' - ' + kind;
      menuItems.push(
        <h5 className="writer-dropdown-menu-title">{sectionTitle}</h5>
      );
      menuItems.push(
        ...tableApps
          .filter(
            (app) =>
              app.name === name &&
              ((app.kind && app.kind === kind) ||
                (!app.kind && kind === PRODUCING))
          )
          .map((app) => {
            const menuItemClassName =
              ++appsDefinedCount === tableApps.length
                ? 'writer-dropdown-menu-item last-item'
                : '';
            return getMenuItem(app, menuItemClassName);
          })
      );
      if (kindIdx + 1 < appKinds.length || nameIdx + 1 < appNames.length) {
        menuItems.push(<MenuItem divider />);
      }
    });
  });

  const avatarLabel = isAirflowOrDatabricksApp(tableApps[0].name)
    ? tableApps[0].name
    : APPLICATIONS_LABEL;
  return (
    <Dropdown className="header-link writer-dropdown" id="writer-dropdown">
      <Dropdown.Toggle className="writer-dropdown-button">
        <AvatarLabel
          label={avatarLabel}
          src={image}
          round={isAirflowOrDatabricksApp(tableApps[0].name)}
        />
      </Dropdown.Toggle>
      <Dropdown.Menu className="writer-dropdown-menu">
        {menuItems}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default WriterDropdown;
