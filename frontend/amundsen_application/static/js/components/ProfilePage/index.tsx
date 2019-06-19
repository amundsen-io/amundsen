import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
import * as Avatar from 'react-avatar';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import Breadcrumb from 'components/common/Breadcrumb';
import Flag from 'components/common/Flag';
import Tabs from 'components/common/Tabs';

import { GlobalState } from 'ducks/rootReducer';
import { getUserById, getUserOwn, getUserRead } from 'ducks/user/reducer';
import { PeopleUser, Resource } from 'interfaces';
import { GetUserRequest, GetUserOwnRequest, GetUserReadRequest } from 'ducks/user/types';

import './styles.scss';
import ResourceList from 'components/common/ResourceList';
import { GetBookmarksForUserRequest } from 'ducks/bookmark/types';
import { getBookmarksForUser } from 'ducks/bookmark/reducer';

import {
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
  getUserById: (userId: string) => GetUserRequest;
  getUserOwn: (userId: string) => GetUserOwnRequest;
  getUserRead: (userId: string) => GetUserReadRequest;
  getBookmarksForUser: (userId: string) => GetBookmarksForUserRequest;
}

export type ProfilePageProps = StateFromProps & DispatchFromProps;

export class ProfilePage extends React.Component<ProfilePageProps> {
  private userId: string;

  constructor(props) {
    super(props);

    const { match } = props;
    const params = match.params;
    this.userId = params && params.userId ? params.userId : '';
  }

  componentDidMount() {
    this.props.getUserById(this.userId);
    this.props.getUserOwn(this.userId);
    this.props.getUserRead(this.userId);
    this.props.getBookmarksForUser(this.userId);
  }

  getUserId = () => {
    return this.userId;
  };


  getTabContent = (resource: Resource[], source: string, label: string) => {
    // TODO: consider moving logic for empty content into Tab component
    if (resource.length === 0) {
      return (
        <div className="empty-tab-message">
          <label>User has no { label } resources.</label>
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
      content: this.getTabContent(read, READ_SOURCE, READ_LABEL),
      key: READ_TAB_KEY,
      title: `${READ_TAB_TITLE} (${read.length})`,
    });
    tabInfo.push({
      content: this.getTabContent(bookmarks, BOOKMARKED_SOURCE, BOOKMARKED_LABEL),
      key: BOOKMARKED_TAB_KEY,
      title: `${BOOKMARKED_TAB_TITLE} (${bookmarks.length})`,
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
        <div className="container profile-page">
          <div className="row">
            <div className="col-xs-12 col-md-offset-1 col-md-10">
              {/* remove hardcode to home when this page is ready for production */}
              <Breadcrumb path="/" text="Home" />
              {/* TODO - Consider making this part a separate component */}
              <div className="profile-header">
                  <div id="profile-avatar" className="profile-avatar">
                    {
                      // default Avatar looks a bit jarring -- intentionally not rendering if no display_name
                      user.display_name && user.display_name.length > 0 &&
                      <Avatar name={user.display_name} size={74} round={true} />
                    }
                  </div>
                  <div className="profile-details">
                    <div id="profile-title" className="profile-title">
                      <h1>{ user.display_name }</h1>
                      {
                        (!user.is_active) &&
                        <Flag caseType="sentenceCase" labelStyle="label-danger" text="Alumni"/>
                      }
                    </div>
                    {
                      user.role_name && user.team_name &&
                      <label id="user-role">{ `${user.role_name} on ${user.team_name}` }</label>
                    }
                    {
                      user.manager_fullname &&
                      <label id="user-manager">{ `Manager: ${user.manager_fullname}` }</label>
                    }
                    <div className="profile-icons">
                      {
                        user.is_active &&
                        <a id="slack-link" href={user.slack_id} className='btn btn-flat-icon' target='_blank'>
                          <img className='icon icon-slack'/>
                          <span>Slack</span>
                        </a>
                      }
                      {
                        user.is_active &&
                        <a id="email-link" href={`mailto:${user.email}`} className='btn btn-flat-icon' target='_blank'>
                          <img className='icon icon-mail'/>
                          <span>{ user.email }</span>
                        </a>
                      }
                      {
                        user.is_active && user.profile_url &&
                        <a id="profile-link" href={user.profile_url} className='btn btn-flat-icon' target='_blank'>
                          <img className='icon icon-users'/>
                          <span>Employee Profile</span>
                        </a>
                      }
                      {
                        user.github_username &&
                        <a id="github-link" href={`https://github.com/${user.github_username}`} className='btn btn-flat-icon' target='_blank'>
                          <img className='icon icon-github'/>
                          <span>Github</span>
                        </a>
                      }
                    </div>
                  </div>
              </div>
              <div id="profile-tabs" className="profile-tabs">
                <Tabs tabs={ this.generateTabInfo() } defaultTab={ READ_TAB_KEY } />
              </div>
            </div>
          </div>
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
  return bindActionCreators({ getUserById, getUserOwn, getUserRead, getBookmarksForUser }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(ProfilePage);
