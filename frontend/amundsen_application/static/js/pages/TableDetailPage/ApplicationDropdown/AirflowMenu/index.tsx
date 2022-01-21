// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';

import { TableApp } from 'interfaces';
import {
  AIRFLOW,
  DAG_LABEL,
  NOT_AVAILABLE_VALUE,
  TASK_LABEL,
  DELAY_SHOW_POPOVER_MS,
} from '../constants';
import '../styles.scss';

export interface AirflowMenuProps {
  tableApps: TableApp[];
  getSortedAppKinds: (apps: TableApp[]) => string[];
  hasSameNameAndKind: (app: TableApp, name: string, kind: string) => boolean;
  handleClick: (event) => void;
}

const getMenuItem = (app: TableApp, handleClick) => {
  const [dagId, ...task] = app.id.split('/');
  const taskId = task.join('/');

  return (
    <OverlayTrigger
      key={app.id}
      trigger={['hover', 'focus']}
      placement="top"
      delayShow={DELAY_SHOW_POPOVER_MS}
      overlay={<Popover id="popover-trigger-hover-focus">{app.id}</Popover>}
    >
      <MenuItem
        href={app.application_url}
        onClick={handleClick}
        target="_blank"
        rel="noopener noreferrer"
      >
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
      </MenuItem>
    </OverlayTrigger>
  );
};

const AirflowMenu: React.FC<AirflowMenuProps> = ({
  tableApps,
  getSortedAppKinds,
  hasSameNameAndKind,
  handleClick,
}: AirflowMenuProps) => {
  // Group the applications in the dropdown by kind
  let menuItems: React.ReactNode[] = [];
  const appKinds = getSortedAppKinds(tableApps);
  appKinds.forEach((kind, kindIdx) => {
    menuItems = [
      ...menuItems,
      <h5 key={kind} className="application-dropdown-menu-title">
        {kind}
      </h5>,
      ...tableApps
        .filter((app) => hasSameNameAndKind(app, AIRFLOW, kind))
        .map((app) => getMenuItem(app, handleClick)),
    ];

    const isLastApp = kindIdx + 1 < appKinds.length;
    if (isLastApp) {
      menuItems = [...menuItems, <MenuItem divider />];
    }
  });

  return <>{menuItems}</>;
};

export default AirflowMenu;
