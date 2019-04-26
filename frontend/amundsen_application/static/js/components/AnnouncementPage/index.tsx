import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
// TODO - Consider an alternative to react-sanitized-html (large filesize)
import SanitizedHTML from 'react-sanitized-html';

import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import { GlobalState } from 'ducks/rootReducer';
import { AnnouncementsGetRequest } from 'ducks/announcements/types';
import { announcementsGet } from 'ducks/announcements/reducer';
import { AnnouncementPost } from './types';

interface AnnouncementPageState {
  posts: AnnouncementPost[];
}

export interface StateFromProps {
  posts: AnnouncementPost[];
}

export interface DispatchFromProps {
  announcementsGet: () => AnnouncementsGetRequest;
}

export type AnnouncementPageProps = StateFromProps & DispatchFromProps;

export class AnnouncementPage extends React.Component<AnnouncementPageProps, AnnouncementPageState> {
  constructor(props) {
    super(props);

    this.state = {
      posts: this.props.posts,
    };
  }

  componentDidMount() {
    this.props.announcementsGet();
  }

  createPost(post: AnnouncementPost, postIndex: number) {
    return (
      <div key={`post:${postIndex}`} className='post-container'>
        <div className='post-header'>
          <div className='post-title'>{post.title}</div>
          <div className='post-date'>{post.date}</div>
        </div>
        <div className='post-content'>
          <SanitizedHTML html={post.html_content} />
        </div>
      </div>
    );
  }

  createPosts() {
    return this.state.posts.map((post, index) => {
      return this.createPost(post, index)
    });
  }

  render() {
    return (
      <DocumentTitle title="Announcements - Amundsen">
        <div className="container announcement-container">
          <div className="row">
            <div className="col-xs-12">
              <div id="announcement-header" className="announcement-header">
                Announcements
              </div>
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
  return bindActionCreators({ announcementsGet } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(AnnouncementPage);
