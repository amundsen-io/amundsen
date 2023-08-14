// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';

import AvatarLabel from 'components/AvatarLabel';
import { TableSource } from 'interfaces';
import { 
  DELAY_SHOW_POPOVER_MS,
  SOURCE_TYPE_TO_NAME,
  SOURCE_TYPE_TO_IMAGE
} from '../constants';
import '../styles.scss';

export interface GenericMenuProps {
  tableSources: TableSource[];
  // getSortedSources: (sources: TableSource[]) => string[];
  // hasSameNameAndKind: (source: TableSource, name: string, kind: string) => boolean;
  handleClick: (event) => void;
}

const getMenuItem = (source: TableSource, href, handleClick) => (
  <OverlayTrigger
    key={source.source}
    trigger={['hover', 'focus']}
    placement="top"
    delayShow={DELAY_SHOW_POPOVER_MS}
    overlay={<Popover id="popover-trigger-hover-focus">{source.source}</Popover>}
  >    
    <MenuItem
      href={href}
      onClick={handleClick}
      target="_blank"
      rel="noopener noreferrer"
    >
      <div className="source-dropdown-menu-item-row">
        <span className="menu-item-content">{source.source}</span>
      </div>
    </MenuItem>
  </OverlayTrigger>
);

const GenericMenu: React.FC<GenericMenuProps> = ({
  tableSources,
  handleClick,
}: GenericMenuProps) => {
  let menuItems: React.ReactNode[] = [];

  tableSources.forEach((source, idx) => {
    let href = source.source;
    if (source.source != null && !source.source.startsWith("http")) {
      href = null;
    }

    menuItems = [
      ...menuItems,
      // <h5 key={source.source_type} className="application-dropdown-menu-title">
      //   {SOURCE_TYPE_TO_NAME[source.source_type]}
      // </h5>,
      <AvatarLabel
        label={SOURCE_TYPE_TO_NAME[source.source_type]}
        src={SOURCE_TYPE_TO_IMAGE[source.source_type]}
        round={true}
      />,
      getMenuItem(source, href, handleClick),
    ];
  });

  return <>{menuItems}</>;
};

export default GenericMenu;
