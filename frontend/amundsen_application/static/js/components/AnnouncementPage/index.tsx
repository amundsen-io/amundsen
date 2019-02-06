import * as React from 'react';
import * as DocumentTitle from 'react-document-title';
// TODO - Consider an alternative to react-sanitized-html (large filesize)
import SanitizedHTML from 'react-sanitized-html';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import { AnnouncementsGetRequest } from "../../ducks/announcements/reducer";
import { AnnouncementPost } from "./types";

interface AnnouncementPageState {
  posts: AnnouncementPost[];
}

export interface StateFromProps {
  posts: AnnouncementPost[];
}

export interface DispatchFromProps {
  announcementsGet: () => AnnouncementsGetRequest;
}

type AnnouncementPageProps = StateFromProps & DispatchFromProps;

class AnnouncementPage extends React.Component<AnnouncementPageProps, AnnouncementPageState> {
  constructor(props) {
    super(props);

    this.state = {
      posts: this.props.posts,
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const { posts } = nextProps;
    return { posts };
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

  render() {
    return (
      <DocumentTitle title="Announcements - Amundsen">
        <div className="container announcement-container">
          <div className="row">
            <div className="col-xs-12">
              <div className="announcement-header">
                Announcements
              </div>
              <hr />
              <div className='announcement-content'>
                {
                  this.state.posts.map((post, index) => {
                    return this.createPost(post, index)
                  })
                }
              </div>
            </div>
          </div>
        </div>
      </DocumentTitle>
    );
  }
}

export default AnnouncementPage;
