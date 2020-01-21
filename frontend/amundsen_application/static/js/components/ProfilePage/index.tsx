import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as Avatar from 'react-avatar';
import { connect } from 'react-redux';
import { RouteComponentProps, withRouter } from 'react-router';
import { bindActionCreators } from 'redux';
import * as qs from 'simple-query-string';

import Breadcrumb from 'components/common/Breadcrumb';
import Flag from 'components/common/Flag';
import Tabs from 'components/common/Tabs';

import { GlobalState } from 'ducks/rootReducer';
import { getUser, getUserOwn, getUserRead } from 'ducks/user/reducer';
import { PeopleUser, Resource } from 'interfaces';
import { GetUserRequest, GetUserOwnRequest, GetUserReadRequest } from 'ducks/user/types';

import './styles.scss';
import ResourceList from 'components/common/ResourceList';
import { GetBookmarksForUserRequest } from 'ducks/bookmark/types';
import { getBookmarksForUser } from 'ducks/bookmark/reducer';

import {
  AVATAR_SIZE,
  BOOKMARKED_LABEL,
  BOOKMARKED_SOURCE,
  BOOKMARKED_TAB_KEY,
  BOOKMARKED_TAB_TITLE,
  ITEMS_PER_PAGE, OWNED_LABEL,
  OWNED_SOURCE, OWNED_TAB_KEY,
  OWNED_TAB_TITLE, READ_LABEL,
  READ_SOURCE, READ_TAB_KEY,
  READ_TAB_TITLE,
} from './constants';

interface StateFromProps {
  bookmarks: Resource[];
  user: PeopleUser;
  own: Resource[];
  read: Resource[];
}

interface DispatchFromProps {
  getUserById: (userId: string, index?: number, source?: string) => GetUserRequest;
  getUserOwn: (userId: string) => GetUserOwnRequest;
  getUserRead: (userId: string) => GetUserReadRequest;
  getBookmarksForUser: (userId: string) => GetBookmarksForUserRequest;
}

export interface RouteProps {
  userId: string;
}

interface ProfilePageState {
  userId: string;
}

export type ProfilePageProps = StateFromProps & DispatchFromProps & RouteComponentProps<RouteProps>;

export class ProfilePage extends React.Component<ProfilePageProps, ProfilePageState> {

  constructor(props) {
    super(props);
    this.state = { userId: props.match.params.userId }
  }

  componentDidMount() {
    this.loadUserInfo(this.state.userId);
  }

  componentDidUpdate() {
    const userId = this.props.match.params.userId;
    if (userId !== this.state.userId) {
      this.setState({ userId });
      this.loadUserInfo(userId);
    }
  }

  loadUserInfo = (userId: string) => {
    const { index, source } = this.getLoggingParams(this.props.location.search);
    this.props.getUserById(userId, index, source);
    this.props.getUserOwn(userId);
    this.props.getUserRead(userId);
    this.props.getBookmarksForUser(userId);
  };

  getLoggingParams = (search: string) => {
    const params = qs.parse(search);
    const index = params['index'];
    const source = params['source'];
    // Remove logging params from URL
    if (source !== undefined || index !== undefined) {
      window.history.replaceState({}, '', `${window.location.origin}${window.location.pathname}`);
    }
    return { index, source };
  };


  getTabContent = (resource: Resource[], source: string, label: string) => {
    // TODO: consider moving logic for empty content into Tab component
    if (resource.length === 0) {
      return (
        <div className="empty-tab-message body-placeholder">
          User has no { label } resources.
        </div>
      );
    }
    return (
      <ResourceList
        allItems={ resource }
        source={ source }
        itemsPerPage={ ITEMS_PER_PAGE }
      />
    )
  };

  generateTabInfo = () => {
    const tabInfo = [];
    const { bookmarks, read, own } = this.props;

    tabInfo.push({
      content: this.getTabContent(bookmarks, BOOKMARKED_SOURCE, BOOKMARKED_LABEL),
      key: BOOKMARKED_TAB_KEY,
      title: `${BOOKMARKED_TAB_TITLE} (${bookmarks.length})`,
    });
    tabInfo.push({
      content: this.getTabContent(read, READ_SOURCE, READ_LABEL),
      key: READ_TAB_KEY,
      title: `${READ_TAB_TITLE} (${read.length})`,
    });
    tabInfo.push({
      content: this.getTabContent(own, OWNED_SOURCE, OWNED_LABEL),
      key: OWNED_TAB_KEY,
      title: `${OWNED_TAB_TITLE} (${own.length})`,
    });

    return tabInfo;
  };

  /* TODO: Add support to direct to 404 page for edgecase of someone typing in
     or pasting in a bad url. This would be consistent with TableDetail page behavior */
  render() {
    const user = this.props.user;
    return (
      <DocumentTitle title={ `${user.display_name} - Amundsen Profile` }>
        <div className="resource-detail-layout profile-page">
          <header className="resource-header">
            <div className="header-section">
              <Breadcrumb />
              <div id="profile-avatar" className="profile-avatar">
                {
                  user.display_name && user.display_name.length > 0 &&
                  <Avatar name={user.display_name} size={AVATAR_SIZE} round={true} />
                }
              </div>
            </div>

            <div className="header-section header-title">
              <h3 className="header-title-text truncated">
                { user.display_name }
                {
                  (!user.is_active) &&
                  <Flag caseType="sentenceCase" labelStyle="danger" text="Alumni"/>
                }
              </h3>
              <div className="body-3">
                <ul className="header-bullets">
                  {
                    user.role_name &&
                    <li id="user-role">{ user.role_name }</li>
                  }
                  {
                    user.team_name &&
                    <li id="team-name">{ user.team_name }</li>
                  }
                  {
                    user.manager_fullname &&
                    <li id="user-manager">{ `Manager: ${user.manager_fullname}` }</li>
                  }
                </ul>
              </div>
            </div>
            <div className="header-section header-links">
              {/*{*/}
              {/*  // TODO - Implement deep links to open Slack *!/*/}
              {/*  user.is_active && user.slack_id &&*/}
              {/*  <a id="slack-link" href={user.slack_id} className='btn btn-flat-icon header-link' target='_blank'>*/}
              {/*    <img className='icon icon-dark icon-slack'/>*/}
              {/*    <span className="body-2">Slack</span>*/}
              {/*  </a>*/}
              {/*}*/}
              {
                user.is_active &&
                <a id="email-link" href={`mailto:${user.email}`} className='btn btn-flat-icon header-link' target='_blank'>
                  <img className='icon icon-dark icon-mail'/>
                  <span className="body-2">{ user.email }</span>
                </a>
              }
              {
                user.is_active && user.profile_url &&
                <a id="profile-link" href={user.profile_url} className='btn btn-flat-icon header-link' target='_blank'>
                  <img className='icon icon-dark icon-users'/>
                  <span className="body-2">Employee Profile</span>
                </a>
              }
              {
                user.github_username &&
                <a id="github-link" href={`https://github.com/${user.github_username}`} className='btn btn-flat-icon header-link' target='_blank'>
                  <img className='icon icon-dark icon-github'/>
                  <span className="body-2">Github</span>
                </a>
              }
            </div>
          </header>
          <main>
            <div className="profile-tabs">
              <Tabs tabs={ this.generateTabInfo() } defaultTab={ BOOKMARKED_TAB_KEY } />
            </div>
          </main>
        </div>
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    user: state.user.profile.user,
    own: state.user.profile.own,
    read: state.user.profile.read,
    bookmarks: state.bookmarks.bookmarksForUser,
  }
};

export const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({ getUserOwn, getUserRead, getBookmarksForUser, getUserById: getUser }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(withRouter(ProfilePage));
