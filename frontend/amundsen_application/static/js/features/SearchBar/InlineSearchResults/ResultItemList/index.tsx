// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { ResourceType } from 'interfaces';
import { logClick } from 'utils/analytics';

import {
  RESULT_LIST_FOOTER_PREFIX,
  RESULT_LIST_FOOTER_SUFFIX,
} from '../constants';

import ResultItem from './ResultItem';

export interface SuggestedResult {
  href: string;
  iconClass: string;
  subtitle: string;
  titleNode: React.ReactNode;
  type: string;
}

export interface ResultItemListProps {
  onItemSelect: (resourceType: ResourceType, updateUrl?: boolean) => void;
  resourceType: ResourceType;
  searchTerm: string;
  suggestedResults: SuggestedResult[];
  title: string;
  totalResults: number;
}

class ResultItemList extends React.Component<ResultItemListProps, {}> {
  generateFooterLinkText = () => {
    const { totalResults, title } = this.props;

    return `${RESULT_LIST_FOOTER_PREFIX} ${totalResults} ${title} ${RESULT_LIST_FOOTER_SUFFIX}`;
  };

  onViewAllResults = (e) => {
    logClick(e);
    const { resourceType, onItemSelect } = this.props;

    onItemSelect(resourceType, true);
  };

  renderResultItems = (results: SuggestedResult[]) => {
    const onResultItemSelect = (e) => {
      logClick(e);
      const { resourceType, onItemSelect } = this.props;

      onItemSelect(resourceType, true);
    };

    return results.map((item, index) => {
      const { href, iconClass, subtitle, titleNode, type } = item;
      const { resourceType } = this.props;
      const id = `inline-resultitem-${resourceType}:${index}`;

      return (
        <ResultItem
          key={id}
          id={id}
          href={href}
          onItemSelect={onResultItemSelect}
          iconClass={`icon icon-dark ${iconClass}`}
          subtitle={subtitle}
          titleNode={titleNode}
          type={type}
        />
      );
    });
  };

  render = () => {
    const { resourceType, suggestedResults, title } = this.props;

    return (
      <>
        <h3 className="section-title title-3">{title}</h3>
        <ul className="list-group">
          {this.renderResultItems(suggestedResults)}
        </ul>
        {/* eslint-disable jsx-a11y/anchor-is-valid */}
        <a
          id={`inline-resultitem-viewall:${resourceType}`}
          className="section-footer title-3"
          onClick={this.onViewAllResults}
          onKeyDown={this.onViewAllResults}
          target="_blank"
          role="button"
          tabIndex={-1} // TODO: Make navigable with arrow keys or further tab key presses
        >
          {this.generateFooterLinkText()}
        </a>
      </>
    );
  };
}

export default ResultItemList;
