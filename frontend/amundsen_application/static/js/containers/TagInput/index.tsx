import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../ducks/rootReducer";
import { getAllTags } from '../../ducks/tags/reducer';
import { updateTags } from '../../ducks/tableMetadata/reducer';

import TagInput, { ComponentProps, DispatchFromProps, StateFromProps} from '../../components/Tags/TagInput';

export const mapStateToProps = (state: GlobalState) => {
  return {
    allTags: state.tags.allTags,
    isLoading: state.tags.isLoading || state.tableMetadata.isLoadingTags,
    tags: state.tableMetadata.tableData.tags,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ getAllTags, updateTags } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(TagInput);
