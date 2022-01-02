// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown } from 'react-bootstrap';

import AvatarLabel from 'components/AvatarLabel';
import { TableApp } from 'interfaces';
import { logClick } from 'utils/analytics';
import AirflowMenu from './AirflowMenu';
import DatabricksMenu from './DatabricksMenu';
import GenericMenu from './GenericMenu';
import {
  APPLICATIONS_LABEL,
  AIRFLOW,
  DATABRICKS,
  PRODUCING,
  CONSUMING,
  AIRFLOW_LOGO_PATH,
  DATABRICKS_LOGO_PATH,
  GENERIC_APP_LOGO_PATH,
} from './constants';
import './styles.scss';

export interface ApplicationDropdownProps {
  tableApps: TableApp[];
}

const getImagePath = (tableAppName) => {
  switch (tableAppName) {
    case AIRFLOW.toLowerCase():
      return AIRFLOW_LOGO_PATH;
    case DATABRICKS.toLowerCase():
      return DATABRICKS_LOGO_PATH;
    default:
      return GENERIC_APP_LOGO_PATH;
  }
};

const isAirflowOrDatabricksApp = (appName) =>
  appName.toLowerCase() === AIRFLOW.toLowerCase() ||
  appName.toLowerCase() === DATABRICKS.toLowerCase();

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

const getDropdownMenuContents = (tableApps) => {
  const isAirflow = tableApps[0].name.toLowerCase() === AIRFLOW.toLowerCase();
  const isDatabricks =
    tableApps[0].name.toLowerCase() === DATABRICKS.toLowerCase();

  if (isAirflow) {
    return (
      <AirflowMenu
        tableApps={tableApps}
        getSortedAppKinds={getSortedAppKinds}
        hasSameNameAndKind={hasSameNameAndKind}
        handleClick={handleClick}
      />
    );
  }
  if (isDatabricks) {
    return (
      <DatabricksMenu
        tableApps={tableApps}
        getSortedAppKinds={getSortedAppKinds}
        hasSameNameAndKind={hasSameNameAndKind}
        handleClick={handleClick}
      />
    );
  }
  return (
    <GenericMenu
      tableApps={tableApps}
      getSortedAppKinds={getSortedAppKinds}
      hasSameNameAndKind={hasSameNameAndKind}
      handleClick={handleClick}
    />
  );
};

const ApplicationDropdown: React.FC<ApplicationDropdownProps> = ({
  tableApps,
}: ApplicationDropdownProps) => {
  if (tableApps === null || tableApps.length === 0) {
    return null;
  }

  tableApps.sort(sortByNameOrId);

  const image = getImagePath(tableApps[0].name.toLowerCase());
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
        {getDropdownMenuContents(tableApps)}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default ApplicationDropdown;
