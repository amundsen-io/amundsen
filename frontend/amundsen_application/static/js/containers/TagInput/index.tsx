import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../ducks/rootReducer";
import { getAllTags } from '../../ducks/allTags/reducer';
import { updateTags } from '../../ducks/tableMetadata/tags/reducer';

import TagInput, { ComponentProps, DispatchFromProps, StateFromProps} from '../../components/Tags/TagInput';

export const mapStateToProps = (state: GlobalState) => {
  return {
    allTags: state.allTags.allTags,
    isLoading: state.allTags.isLoading || state.tableMetadata.tableTags.isLoading,
    tags: state.tableMetadata.tableTags.tags,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getAllTags, updateTags } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(TagInput);
