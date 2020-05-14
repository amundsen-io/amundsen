import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as Avatar from 'react-avatar';
import { connect } from 'react-redux';
import { RouteComponentProps, withRouter } from 'react-router';
import { bindActionCreators } from 'redux';

import Breadcrumb from 'components/common/Breadcrumb';
import Flag from 'components/common/Flag';
import TabsComponent from 'components/common/TabsComponent';

import { GlobalState } from 'ducks/rootReducer';
import { getUser, getUserOwn, getUserRead } from 'ducks/user/reducer';
import { PeopleUser, Resource, ResourceType, ResourceDict } from 'interfaces';
import { GetUserRequest, GetUserOwnRequest, GetUserReadRequest } from 'ducks/user/types';

import './styles.scss';
import ResourceList from 'components/common/ResourceList';
import { GetBookmarksForUserRequest } from 'ducks/bookmark/types';
import { getBookmarksForUser } from 'ducks/bookmark/reducer';

import { getDisplayNameByResource, indexDashboardsEnabled } from 'config/config-utils';

import { getLoggingParams } from 'utils/logUtils';

import {
  AVATAR_SIZE,
  BOOKMARKED_LABEL,
  BOOKMARKED_SOURCE,
  BOOKMARKED_TITLE_PREFIX,
  EMPTY_TEXT_PREFIX,
  FOOTER_TEXT_PREFIX,
  ITEMS_PER_PAGE,
  OWNED_LABEL,
  OWNED_SOURCE,
  OWNED_TITLE_PREFIX,
  READ_LABEL,
  READ_SOURCE,
  READ_TITLE_PREFIX
} from './constants';

interface ResourceRelation {
  bookmarks: Resource[];
  own: Resource[];
  read: Resource[];
}
interface StateFromProps {
  user: PeopleUser;
  resourceRelations: ResourceDict<ResourceRelation>;
}

interface DispatchFromProps {
  getUserById: (userId: string, index?: string, source?: string) => GetUserRequest;
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
    const { index, source } = getLoggingParams(this.props.location.search);
    this.props.getUserById(userId, index, source);
    this.props.getUserOwn(userId);
    this.props.getUserRead(userId);
    this.props.getBookmarksForUser(userId);
  };

  generateTabContent = (resource: ResourceType) => {
    const { bookmarks = [], own = [], read = [] } = this.props.resourceRelations[resource];
    const resourceLabel = getDisplayNameByResource(resource);
    return (
      <>
        <ResourceList
          allItems={ own }
          emptyText={`${EMPTY_TEXT_PREFIX} ${OWNED_LABEL} ${resourceLabel}.`}
          footerTextCollapsed={`${FOOTER_TEXT_PREFIX} ${own.length} ${OWNED_LABEL} ${resourceLabel}`}
          itemsPerPage={ ITEMS_PER_PAGE }
          source={ OWNED_SOURCE }
          title={`${OWNED_TITLE_PREFIX} (${own.length})`}
        />
        <ResourceList
          allItems={ bookmarks }
          emptyText={`${EMPTY_TEXT_PREFIX} ${BOOKMARKED_LABEL} ${resourceLabel}.`}
          footerTextCollapsed={`${FOOTER_TEXT_PREFIX} ${bookmarks.length} ${BOOKMARKED_LABEL} ${resourceLabel}`}
          itemsPerPage={ ITEMS_PER_PAGE }
          source={ BOOKMARKED_SOURCE }
          title={`${BOOKMARKED_TITLE_PREFIX} (${bookmarks.length})`}
        />
        {
          /* Frequently Used currently not supported for dashboards */
          resource === ResourceType.table &&
          <ResourceList
            allItems={ read }
            emptyText={`${EMPTY_TEXT_PREFIX} ${READ_LABEL} ${resourceLabel}.`}
            footerTextCollapsed={`${FOOTER_TEXT_PREFIX} ${read.length} ${READ_LABEL} ${resourceLabel}`}
            itemsPerPage={ ITEMS_PER_PAGE }
            source={ READ_SOURCE }
            title={`${READ_TITLE_PREFIX}  (${read.length})`}
          />
        }
      </>
    )
  };

  generateTabKey = (resource: ResourceType) => {
    return `tab:${resource}`;
  };

  generateTabTitle = (resource: ResourceType) => {
    const { bookmarks = [], own = [], read = [] } = this.props.resourceRelations[resource];
    const totalCount = bookmarks.length + own.length + read.length;
    return `${getDisplayNameByResource(resource)} (${totalCount})`;
  };

  generateTabInfo = () => {
    const tabInfo = [];

    tabInfo.push({
      content: this.generateTabContent(ResourceType.table),
      key: this.generateTabKey(ResourceType.table),
      title: this.generateTabTitle(ResourceType.table)
    })

    if (indexDashboardsEnabled()) {
      tabInfo.push({
        content: this.generateTabContent(ResourceType.dashboard),
        key: this.generateTabKey(ResourceType.dashboard),
        title: this.generateTabTitle(ResourceType.dashboard)
      })
    }

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
                  <span className="email-link-label body-2">{ user.email }</span>
                </a>
              }
              {
                user.is_active && user.profile_url &&
                <a id="profile-link" href={user.profile_url} className='btn btn-flat-icon header-link' target='_blank'>
                  <span className='icon icon-dark icon-users'/>
                  <span className="profile-link-label body-2">Employee Profile</span>
                </a>
              }
              {
                user.github_username &&
                <a id="github-link" href={`https://github.com/${user.github_username}`} className='btn btn-flat-icon header-link' target='_blank'>
                  <img className='icon icon-dark icon-github'/>
                  <span className="github-link-label body-2">Github</span>
                </a>
              }
            </div>
          </header>
          <main className="profile-body">
            <TabsComponent tabs={ this.generateTabInfo() } defaultTab={ this.generateTabKey(ResourceType.table) } />
          </main>
        </div>
      </DocumentTitle>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    user: state.user.profile.user,
    resourceRelations: {
      [ResourceType.table]: {
        bookmarks: state.bookmarks.bookmarksForUser[ResourceType.table],
        own: state.user.profile.own[ResourceType.table],
        read: state.user.profile.read,
      },
      [ResourceType.dashboard]: {
        bookmarks: state.bookmarks.bookmarksForUser[ResourceType.dashboard],
        own: state.user.profile.own[ResourceType.dashboard],
        read: [],
      }
    }
  }
};

export const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({ getUserOwn, getUserRead, getBookmarksForUser, getUserById: getUser }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(withRouter(ProfilePage));
