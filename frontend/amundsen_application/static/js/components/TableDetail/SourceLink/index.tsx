import * as React from 'react';

import { logClick } from 'ducks/utilMethods';
import AvatarLabel from 'components/common/AvatarLabel';
import { TableSource } from 'interfaces';

export interface SourceLinkProps {
  tableSource: TableSource;
}

const SourceLink: React.SFC<SourceLinkProps> = ({ tableSource }) => {
  if (tableSource === null || tableSource.source === null) return null;

  const image = (tableSource.source_type === 'github')? '/static/images/github.png': '';
  return (
    <a
      className="header-link"
      href={ tableSource.source }
      id="explore-source"
      onClick={ logClick }
      target='_blank'
    >
      <AvatarLabel label={ tableSource.source_type } src={ image }/>
    </a>
  );
};

export default SourceLink;
