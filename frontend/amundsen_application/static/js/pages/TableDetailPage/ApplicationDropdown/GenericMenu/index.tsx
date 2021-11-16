// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';

import { TableApp } from 'interfaces';
import { DELAY_SHOW_POPOVER_MS } from '../constants';
import '../styles.scss';

export interface GenericMenuProps {
  tableApps: TableApp[];
  getSortedAppKinds: (apps: TableApp[]) => string[];
  hasSameNameAndKind: (app: TableApp, name: string, kind: string) => boolean;
  handleClick: (event) => void;
}

const getMenuItem = (app: TableApp, handleClick) => (
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
      <div className="application-dropdown-menu-item-row">
        <span className="menu-item-content">{app.id}</span>
      </div>
    </MenuItem>
  </OverlayTrigger>
);

const GenericMenu: React.FC<GenericMenuProps> = ({
  tableApps,
  getSortedAppKinds,
  hasSameNameAndKind,
  handleClick,
}: GenericMenuProps) => {
  const appNames: string[] = [...new Set(tableApps.map(({ name }) => name))];

  // Group the applications in the dropdown by name then kind
  let menuItems: React.ReactNode[] = [];
  appNames.forEach((name, nameIdx) => {
    const appKinds = getSortedAppKinds(
      tableApps.filter((app) => app.name === name)
    );
    appKinds.forEach((kind) => {
      const sectionTitle = name + ' - ' + kind;
      menuItems = [
        ...menuItems,
        <h5 key={sectionTitle} className="application-dropdown-menu-title">
          {sectionTitle}
        </h5>,
        ...tableApps
          .filter((app) => hasSameNameAndKind(app, name, kind))
          .map((app) => getMenuItem(app, handleClick)),
      ];

      const isLastApp = nameIdx + 1 < appNames.length;
      if (isLastApp) {
        menuItems = [...menuItems, <MenuItem divider />];
      }
    });
  });

  return <>{menuItems}</>;
};

export default GenericMenu;
