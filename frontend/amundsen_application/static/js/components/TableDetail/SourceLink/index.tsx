// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import {
  getDescriptionSourceDisplayName,
  getDescriptionSourceIconPath,
} from 'config/config-utils';
import { logClick } from 'ducks/utilMethods';
import AvatarLabel from 'components/common/AvatarLabel';
import { TableSource } from 'interfaces';

export interface SourceLinkProps {
  tableSource: TableSource;
}

const SourceLink: React.FC<SourceLinkProps> = ({
  tableSource,
}: SourceLinkProps) => {
  if (tableSource === null || tableSource.source === null) return null;

  const image = getDescriptionSourceIconPath(tableSource.source_type);

  const displayName = getDescriptionSourceDisplayName(tableSource.source_type);

  return (
    <a
      className="header-link"
      href={tableSource.source}
      id="explore-source"
      onClick={logClick}
      target="_blank"
      rel="noreferrer"
    >
      <AvatarLabel
        label={getDescriptionSourceDisplayName(tableSource.source_type)}
        src={getDescriptionSourceIconPath(tableSource.source_type)}
      />
    </a>
  );
};

export default SourceLink;
