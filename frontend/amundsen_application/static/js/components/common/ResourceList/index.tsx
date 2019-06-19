import * as React from 'react';
import Pagination from 'react-js-pagination';
import ResourceListItem from 'components/common/ResourceListItem';
import { Resource } from 'interfaces';
import { ITEMS_PER_PAGE, PAGINATION_PAGE_RANGE } from './constants';


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
}

interface ResourceListState {
  activePage: number;
}

class ResourceList extends React.Component<ResourceListProps, ResourceListState> {
  public static defaultProps: Partial<ResourceListProps> = {
    paginate: true,
    itemsPerPage: ITEMS_PER_PAGE,
  };

  constructor(props) {
    super(props);
    this.state = { activePage: 0 };
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


  render() {
    const { allItems, slicedItems, itemsPerPage, paginate, source } = this.props;
    const activePage = this.props.activePage !== undefined ? this.props.activePage : this.state.activePage;
    const itemsCount = this.props.slicedItemsCount || allItems.length;
    const startIndex = itemsPerPage * activePage;

    let itemsToRender = slicedItems || allItems;
    if (paginate && allItems) {
      itemsToRender = allItems.slice(startIndex, startIndex + itemsPerPage);
    }

    return (
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
      </>
    );
  }
}

export default ResourceList;
