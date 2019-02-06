import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../ducks/rootReducer";
import { executeSearch, ExecuteSearchRequest } from '../../ducks/search/reducer';
import { getPopularTables, GetPopularTablesRequest } from '../../ducks/popularTables/reducer';

import SearchPage, { DispatchFromProps, StateFromProps } from '../../components/SearchPage';

export const mapStateToProps = (state: GlobalState) => {
  return {
    pageIndex: state.search.pageIndex,
    popularTables: state.popularTables,
    searchResults: state.search.searchResults,
    searchTerm: state.search.searchTerm,
    totalResults: state.search.totalResults,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ executeSearch, getPopularTables } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(SearchPage);
