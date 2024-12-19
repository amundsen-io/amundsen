// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { ResourceType } from 'interfaces';
import { logClick } from 'utils/analytics';

import { LogSearchEventRequest } from 'ducks/log/types';
import { bindActionCreators } from 'redux';
import { logSearchEvent } from 'ducks/log/reducer';
import { connect } from 'react-redux';
import ResultItem from './ResultItem';
import {
  RESULT_LIST_FOOTER_PREFIX,
  RESULT_LIST_FOOTER_SUFFIX,
} from '../constants';

export interface SuggestedResult {
  href: string;
  iconClass: string;
  subtitle: string;
  titleNode: React.ReactNode;
  type: string;
}

export interface OwnProps {
  onItemSelect: (resourceType: ResourceType, updateUrl?: boolean) => void;
  resourceType: ResourceType;
  searchTerm: string;
  suggestedResults: SuggestedResult[];
  title: string;
  totalResults: number;
}

export interface DispatchFromProps {
  logSearchEvent: (
    resourceLink: string,
    resourceType: ResourceType,
    source: string,
    index: number,
    event: any,
    inline: boolean,
    extra?: { [key: string]: any }
  ) => LogSearchEventRequest;
}

export interface ResultItemListProps extends OwnProps, DispatchFromProps {}

export class ResultItemList extends React.Component<ResultItemListProps, {}> {
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
    const onResultItemSelect = (e, item, index) => {
      const { resourceType, onItemSelect, logSearchEvent } = this.props;

      logSearchEvent(item.href, resourceType, resourceType, index, e, true);

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
          onItemSelect={(e) => onResultItemSelect(e, item, index)}
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

export const mapDispatchToProps = (dispatch: any): DispatchFromProps => {
  const dispatchableActions: DispatchFromProps = bindActionCreators(
    {
      logSearchEvent,
    },
    dispatch
  );

  return dispatchableActions;
};

export default connect<{}, DispatchFromProps, OwnProps>(
  null,
  mapDispatchToProps
)(ResultItemList);
