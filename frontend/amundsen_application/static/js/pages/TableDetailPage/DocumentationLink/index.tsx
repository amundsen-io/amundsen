// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import AvatarLabel from 'components/AvatarLabel';

import { TableDocumentation } from 'interfaces';
import { logClick } from 'utils/analytics';

export interface DocumentationLinkProps {
  tableDocumentation: TableDocumentation;
}

const DocumentationLink: React.FC<DocumentationLinkProps> = ({
  tableDocumentation,
}: DocumentationLinkProps) => {
  if (tableDocumentation === null || tableDocumentation.link === null) return null;

  return (
    <a
      className="header-link"
      href={tableDocumentation.link}
      id="explore-source"
      onClick={logClick}
      target="_blank"
      rel="noreferrer"
    >
      <AvatarLabel
        label={"Documentation"}
        src={"images/icons/documentation.jpg"}
        round={false}
      />
    </a>
  );
};

export default DocumentationLink;
