import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { GetAnnouncementsRequest } from 'ducks/announcements/types';
import { getAnnouncements } from 'ducks/announcements';

import { AnnouncementPost } from 'interfaces';

import AnnouncementsList from './AnnouncementsList';

export interface StateFromProps {
  isLoading: boolean;
  statusCode: number;
  announcements: AnnouncementPost[];
}

export interface DispatchFromProps {
  announcementsGet: () => GetAnnouncementsRequest;
}

export type AnnouncementContainerProps = StateFromProps & DispatchFromProps;

const OK_STATUS_CODE = 200;

const AnnouncementsListContainer: React.FC<AnnouncementContainerProps> = ({
  announcements,
  announcementsGet,
  isLoading,
  statusCode,
}: AnnouncementContainerProps) => {
  React.useEffect(() => {
    announcementsGet();
  }, []);

  return (
    <AnnouncementsList
      hasError={statusCode !== OK_STATUS_CODE}
      isLoading={isLoading}
      announcements={announcements}
    />
  );
};

export const mapStateToProps = (state: GlobalState) => {
  return {
    announcements: state.announcements.posts,
    isLoading: state.announcements.isLoading,
    statusCode: state.announcements.statusCode,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ announcementsGet: getAnnouncements }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(AnnouncementsListContainer);
