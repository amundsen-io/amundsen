// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import {
  getDescriptionSourceDisplayName,
  getDescriptionSourceIconPath,
} from 'config/config-utils';
import AvatarLabel from 'components/AvatarLabel';

import { ResourceType, ServiceSource, TableSource } from 'interfaces';
import { logClick } from 'utils/analytics';

export interface SourceLinkProps {
  serviceSource: ServiceSource;
}

const SourceLink: React.FC<SourceLinkProps> = ({
    serviceSource,
}: SourceLinkProps) => {
  if (serviceSource === null || serviceSource.source === null) return null;
  return (
    <a
      className="header-link"
      href={serviceSource.source || ""}
      id="explore-source"
      onClick={logClick}
      target="_blank"
      rel="noreferrer"
    >
      <AvatarLabel
        label={getDescriptionSourceDisplayName(serviceSource.source_type)}
        src={getDescriptionSourceIconPath(serviceSource.source_type)}
        round={false}
      />
    </a>
  );
};

export default SourceLink;
