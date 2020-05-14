import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
// TODO - Consider an alternative to react-sanitized-html (large filesize)
import SanitizedHTML from 'react-sanitized-html';

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import { GlobalState } from 'ducks/rootReducer';
import { GetAnnouncementsRequest } from 'ducks/announcements/types';
import { getAnnouncements } from 'ducks/announcements/reducer';
import { AnnouncementPost } from 'interfaces';

export interface StateFromProps {
  posts: AnnouncementPost[];
}

export interface DispatchFromProps {
  announcementsGet: () => GetAnnouncementsRequest;
}

export type AnnouncementPageProps = StateFromProps & DispatchFromProps;

export class AnnouncementPage extends React.Component<AnnouncementPageProps> {
  componentDidMount() {
    this.props.announcementsGet();
  }

  createPost(post: AnnouncementPost, postIndex: number) {
    return (
      <div key={`post:${postIndex}`} className='post-container'>
        <div className='post-header'>
          <div className='post-title title-2'>{post.title}</div>
          <div className='body-secondary-3'>{post.date}</div>
        </div>
        <div className='post-content'>
          <SanitizedHTML html={post.html_content} />
        </div>
      </div>
    );
  }

  createPosts() {
    return this.props.posts.map((post, index) => {
      return this.createPost(post, index)
    });
  }

  render() {
    return (
      <DocumentTitle title="Announcements - Amundsen">
        <div className="container announcement-container">
          <div className="row">
            <div className="col-xs-12">
              <h3 id="announcement-header">Announcements</h3>
              <hr />
              <div id="announcement-content" className='announcement-content'>
                {this.createPosts()}
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
    posts: state.announcements.posts,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ announcementsGet: getAnnouncements } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(AnnouncementPage);
