import * as React from 'react';
import { logClick } from 'ducks/utilMethods';
import { ResourceType } from 'interfaces';

import { SuggestedResult } from '../../InlineSearchResults'
import ResultItem from './ResultItem';

import { RESULT_LIST_FOOTER_PREFIX, RESULT_LIST_FOOTER_SUFFIX } from '../constants';

export interface ResultItemListProps {
  onItemSelect: (resourceType: ResourceType, updateUrl?: boolean) => void;
  resourceType: ResourceType;
  searchTerm: string;
  suggestedResults: SuggestedResult[];
  title: string;
  totalResults: number;
}

class ResultItemList extends React.Component<ResultItemListProps, {}> {
  constructor(props) {
    super(props);
  }

  generateFooterLinkText = () => {
    const { totalResults, title } = this.props;
    return `${RESULT_LIST_FOOTER_PREFIX} ${totalResults} ${title} ${RESULT_LIST_FOOTER_SUFFIX}`;
  }

  onViewAllResults = (e) => {
    logClick(e);
    this.props.onItemSelect(this.props.resourceType, true);
  };

  renderResultItems = (results: SuggestedResult[]) => {
    const onResultItemSelect = (e) => {
      logClick(e);
      this.props.onItemSelect(this.props.resourceType);
    }

    return results.map((item, index) => {
      const { href, iconClass, subtitle, title, type } = item;
      const id = `inline-resultitem-${this.props.resourceType}:${index}`;
      return (
        <ResultItem
          key={id}
          id={id}
          href={href}
          onItemSelect={onResultItemSelect}
          iconClass={`icon icon-dark ${iconClass}`}
          subtitle={subtitle}
          title={title}
          type={type}
        />
      )
    });
  }

  render = () => {
    const { resourceType, suggestedResults, title } = this.props;
    return (
      <>
        <div className="section-title title-3">{title}</div>
        <ul className="list-group">
          { this.renderResultItems(suggestedResults) }
        </ul>
        <a
          id={`inline-resultitem-viewall:${resourceType}`}
          className="section-footer title-3"
          onClick={this.onViewAllResults}
          target='_blank'
        >
          { this.generateFooterLinkText() }
        </a>
      </>
    );
  }
}

export default ResultItemList;
