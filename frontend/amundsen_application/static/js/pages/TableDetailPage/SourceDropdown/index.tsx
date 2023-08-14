// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown } from 'react-bootstrap';

import AvatarLabel from 'components/AvatarLabel';
import { TableSource } from 'interfaces';
import { logClick } from 'utils/analytics';
import GenericMenu from './GenericMenu';
import {
  SOURCES_LABEL,
  GITHUB,
  AWSS3,
  SNOWFLAKE,
  GITHUB_LOGO_PATH,
  AWSS3_LOGO_PATH,
  SNOWFLAKE_LOGO_PATH,
  DATABASE_LOGO_PATH,
  SOURCE
} from './constants';
import './styles.scss';

export interface SourceDropdownProps {
  tableSources: TableSource[];
}

const getImagePath = (tableSourceType) => {
  switch (tableSourceType) {
    case GITHUB.toLowerCase():
      return GITHUB_LOGO_PATH;
    case AWSS3.toLowerCase():
      return AWSS3_LOGO_PATH;
    case SNOWFLAKE.toLowerCase():
      return SNOWFLAKE_LOGO_PATH;
    default:
      return DATABASE_LOGO_PATH;
  }
};

const sortByTypeAndSource = (a, b) =>
  a.source_type.localeCompare(b.source_type) && a.source.localeCompare(b.source);

const handleClick = (event) => {
  event.stopPropagation();
  logClick(event);
};

const getDropdownMenuContents = (tableSources) => {
  return (
    <GenericMenu
      tableSources={tableSources}
      handleClick={handleClick}
    />
  );
};

const SourceDropdown: React.FC<SourceDropdownProps> = ({
  tableSources,
}: SourceDropdownProps) => {
  if (tableSources === null || tableSources.length === 0) {
    return null;
  }

  tableSources.sort(sortByTypeAndSource);

  const image = DATABASE_LOGO_PATH;
  const avatarLabel = SOURCES_LABEL;

  return (
    <Dropdown
      className="header-link sources-dropdown"
      id="sources-dropdown"
      pullRight
    >
      <Dropdown.Toggle className="sources-dropdown-button">
        <AvatarLabel
          label={avatarLabel}
          src={image}
          round={true}
        />
      </Dropdown.Toggle>
      <Dropdown.Menu className="sources-dropdown-menu">
        {getDropdownMenuContents(tableSources)}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default SourceDropdown;
