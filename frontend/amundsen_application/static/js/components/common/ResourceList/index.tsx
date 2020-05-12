import * as React from 'react';
import Pagination from 'react-js-pagination';
import ResourceListItem from 'components/common/ResourceListItem';
import { Resource } from 'interfaces';
import { ITEMS_PER_PAGE, PAGINATION_PAGE_RANGE } from './constants';

import './styles.scss';

export interface ResourceListProps {
  source: string;
  paginate?: boolean;
  itemsPerPage?: number;

  // Choose to use either 'allItems' vs 'slicedItems' depending on if you're passing the entire list
  // of items vs a pre-sliced section of all items.
  allItems?: Resource[];

  // 'slicedItems' and 'slicedItemsCount' should be used together
  slicedItems?: Resource[];
  slicedItemsCount?: number;

  // 'onPagination' and 'activePage' should be used together
  onPagination?: (pageNumber: number) => void;
  activePage?: number;

  customEmptyText?: string;
  customFooterText?: string;
  title?: string;
}

interface ResourceListState {
  activePage: number;
  isExpanded: boolean;
}

class ResourceList extends React.Component<ResourceListProps, ResourceListState> {
  public static defaultProps: Partial<ResourceListProps> = {
    paginate: true,
    itemsPerPage: ITEMS_PER_PAGE,
  };

  constructor(props) {
    super(props);
    this.state = {
      activePage: 0,
      isExpanded: false,
    };
  }

  onPagination = (rawPageNum: number) => {
    const activePage = rawPageNum - 1;
    if (this.props.onPagination !== undefined) {
      // activePage is managed externally via 'props'
      this.props.onPagination(activePage);
    } else {
      // activePage is managed internally via 'state'.
      this.setState({ activePage });
    }
  };

  onViewAllToggle = () => {
    this.setState({ isExpanded: !this.state.isExpanded })
  };

  render() {
    /* TODO ttannis: create render helpers */
    const { allItems, customEmptyText, customFooterText, slicedItems, itemsPerPage, paginate, source, title } = this.props;
    const activePage = this.props.activePage !== undefined ? this.props.activePage : this.state.activePage;
    const itemsCount = this.props.slicedItemsCount || allItems.length;
    const startIndex = itemsPerPage * activePage;

    let itemsToRender = slicedItems || allItems;
    if ((paginate && allItems) || (!this.state.isExpanded && allItems)) {
      itemsToRender = allItems.slice(startIndex, startIndex + itemsPerPage);
    }

    return (
      <div className="resource-list">
        {
          title &&
          <div className="resource-list-title title-3">{title}</div>
        }
        {
          itemsCount === 0 && customEmptyText &&
          <div className="empty-message body-placeholder">
            { customEmptyText }
          </div>
        }
        {
          itemsCount > 0 &&
          <>
            <ul className="list-group">
              {
                itemsToRender.map((item, idx) => {
                  const logging = { source, index: startIndex + idx };
                  return <ResourceListItem item={ item } logging={ logging } key={ idx } />;
                })
              }
            </ul>
            {
              paginate &&
              itemsCount > itemsPerPage &&
              <Pagination
                activePage={ activePage + 1 }
                itemsCountPerPage={ itemsPerPage }
                totalItemsCount={ itemsCount }
                pageRangeDisplayed={ PAGINATION_PAGE_RANGE }
                onChange={ this.onPagination }
              />
            }
            <div className="resource-list-footer">
              {
                !paginate &&
                itemsCount > itemsPerPage &&
                <a
                  onClick={this.onViewAllToggle}
                  target='_blank'
                >
                  { this.state.isExpanded ? "View less" : (customFooterText ? customFooterText : "View all") }
                </a>
              }
            </div>
          </>
        }
      </div>
    );
  }
}

export default ResourceList;
