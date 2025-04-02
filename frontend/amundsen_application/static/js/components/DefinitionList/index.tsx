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
}) => {
  const parseDescription = (description) => {
    switch (typeof description) {
      case 'object':
        return (
          <>
            {Array.isArray(description)
              ? description.map((item) => {
                  const items = Object.keys(item).map((key) => (
                    <div key={key}>
                      <div
                        className="definition-list-term"
                        style={{
                          minWidth: termWidth ? `${termWidth}px` : 'auto',
                        }}
                      >
                        {key}:
                      </div>
                      <div className="definition-list-definition">
                        {parseDescription(item[key])}
                      </div>
                    </div>
                  ));

                  return (
                    <div className="definition-list-items-group">{items}</div>
                  );
                })
              : description}
          </>
        );
      case 'string':
        return <SanitizedHTML html={description} className="definition-text" />;
      default:
        return description;
    }
  };

  return (
    <dl className="definition-list">
      {definitions.map(({ term, description }) => (
        <div className="definition-list-container" key={term}>
          {Array.isArray(description) ? (
            <div className="definition-list-inner-container">
              {parseDescription(description)}
            </div>
          ) : (
            <>
              <dt
                className="definition-list-term"
                style={{ minWidth: termWidth ? `${termWidth}px` : 'auto' }}
              >
                {term}
              </dt>
              <dd className="definition-list-definition">
                {parseDescription(description)}
              </dd>
            </>
          )}
        </div>
      ))}
    </dl>
  );
};

export default DefinitionList;
