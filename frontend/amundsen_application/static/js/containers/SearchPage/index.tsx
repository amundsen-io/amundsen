import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../ducks/rootReducer";
import { executeSearch } from '../../ducks/search/reducer';
import { getPopularTables } from '../../ducks/popularTables/reducer';

import SearchPage, { DispatchFromProps, StateFromProps } from '../../components/SearchPage';

export const mapStateToProps = (state: GlobalState) => {
  return {
    searchTerm: state.search.searchTerm,
    popularTables: state.popularTables,
    tables: state.search.tables,
    users: state.search.users,
    dashboards: state.search.dashboards,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ executeSearch, getPopularTables } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(SearchPage);
