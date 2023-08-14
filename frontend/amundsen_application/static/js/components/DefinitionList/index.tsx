// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import SanitizedHTML from 'react-sanitized-html';

import './styles.scss';

export interface DefinitionType {
  /** Definition term */
  term: string;
  /** Definition body text */
  description: React.ReactNode;
}

export interface DefinitionListProps {
  /** Size to fix the term block, in pixels*/
  termWidth?: number;
  /** List of terms and descriptions to render */
  definitions: DefinitionType[];
}

export const DefinitionList: React.FC<DefinitionListProps> = ({
  definitions,
  termWidth,
}) => (
  <dl className="definition-list">
    {definitions.map(({ term, description }) => (
      <div className="definition-list-container" key={term}>
        <dt
          className="definition-list-term"
          style={{ minWidth: termWidth ? `${termWidth}px` : 'auto' }}
        >
          {term}
        </dt>
        <dd className="definition-list-definition">
          {typeof description === 'string' ? (
            <SanitizedHTML html={description} className="definition-text" />
          ) : (
            description
          )}
        </dd>
      </div>
    ))}
  </dl>
);

export default DefinitionList;
