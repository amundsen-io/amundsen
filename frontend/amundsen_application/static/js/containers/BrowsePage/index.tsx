import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { getAllTags } from '../../ducks/allTags/reducer';

import BrowsePage, { DispatchFromProps, StateFromProps } from '../../components/BrowsePage';
import { GlobalState } from "../../ducks/rootReducer";

export const mapStateToProps = (state: GlobalState) => {
  return {
    allTags: state.allTags.allTags,
    isLoading: state.allTags.isLoading,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getAllTags } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(BrowsePage);
