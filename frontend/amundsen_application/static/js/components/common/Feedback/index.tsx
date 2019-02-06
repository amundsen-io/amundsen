import * as React from 'react';
import {
  RatingFeedbackContainer,
  BugReportFeedbackContainer,
  RequestFeedbackContainer } from '../../../containers/common/Feedback';
import { Button, Panel } from 'react-bootstrap';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

interface FeedbackProps {
  content?: React.SFC<any>,
  title?: string,
}

interface FeedbackState {
  open: boolean,
  feedbackType: FeedbackType,
  content: React.SFC<any>
}

enum FeedbackType {
  Rating,
  Bug,
  Request,
}

export default class Feedback extends React.Component<FeedbackProps, FeedbackState> {
  /* TODO: harcoded string that should be translatable/customizable */
  static defaultProps = {
    content: <RatingFeedbackContainer />,
    title: 'Product Feedback'
  };

  constructor(props) {
    super(props);

    this.toggle = this.toggle.bind(this);

    this.state = {
      open: false,
      content: this.props.content,
      feedbackType: FeedbackType.Rating,
    };
  }

  toggle() {
   this.setState({ open: !this.state.open });
  }

  changeType = (type: FeedbackType) => (e) =>  {
    let content;
    if (type === FeedbackType.Request) {
      content = <RequestFeedbackContainer />;
    } else if (type === FeedbackType.Bug) {
      content = <BugReportFeedbackContainer />;
    } else {
      content = <RatingFeedbackContainer />;
    }
    this.setState({
      content,
      feedbackType: type,
    });
  };

  render() {
    const expandedClass = this.state.open ? 'expanded' : 'collapsed';
    return (
      <div className={`feedback-component ${expandedClass}`}>
        {
          this.state.open &&
          <div>
            <div className="feedback-header">
              <button type="button" className="close" aria-label="Close" onClick={this.toggle}>
                <span aria-hidden="true">&times;</span>
                <span className="sr-only">Close</span>
              </button>
              <div className="title">
                {this.props.title.toUpperCase()}
              </div>
            </div>
            <div className="text-center">
              <div className="btn-group" role="group" aria-label="Feedback Type Selector">
                <button type="button"
                        className={"btn btn-default" + (this.state.feedbackType === FeedbackType.Rating? " active": "")}
                        onClick={this.changeType(FeedbackType.Rating)}>
                  Rating</button>
                <button type="button"
                        className={"btn btn-default" + (this.state.feedbackType === FeedbackType.Bug? " active": "")}
                        onClick={this.changeType(FeedbackType.Bug)}>
                  Bug Report</button>
                <button type="button"
                        className={"btn btn-default" + (this.state.feedbackType === FeedbackType.Request? " active": "")}
                        onClick={this.changeType(FeedbackType.Request)}>
                  Request</button>
              </div>
            </div>
            {this.state.content}
          </div>
        }
        {
          !(this.state.open) &&
          <img className='icon-speech' src='/static/images/icons/Speech.svg' onClick={this.toggle}/>
        }
      </div>
    );
  }
}
