import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../ducks/rootReducer";
import { announcementsGet } from '../../ducks/announcements/reducer';

import AnnouncementPage, { DispatchFromProps, StateFromProps } from '../../components/AnnouncementPage';

export const mapStateToProps = (state: GlobalState) => {
  return {
    posts: state.announcements.posts,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ announcementsGet } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(AnnouncementPage);
