import * as React from 'react';

import BugReportFeedbackForm from './FeedbackForm/BugReportFeedbackForm';
import RatingFeedbackForm from './FeedbackForm/RatingFeedbackForm';
import RequestFeedbackForm from './FeedbackForm/RequestFeedbackForm';

import { Button, Panel } from 'react-bootstrap';

import {
  BUG_REPORT_TEXT,
  BUTTON_CLOSE_TEXT,
  FEEDBACK_TITLE,
  FEEDBACK_TYPE_TEXT,
  RATING_TEXT,
  REQUEST_TEXT,
} from './constants';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface FeedbackProps {
  content?: React.SFC<any>,
  title?: string,
}

interface FeedbackState {
  content: React.SFC<any>,
  feedbackType: FeedbackType,
  isOpen: boolean,
}

export enum FeedbackType {
  Rating,
  Bug,
  Request,
}

export default class Feedback extends React.Component<FeedbackProps, FeedbackState> {
  static defaultProps = {
    content: <RatingFeedbackForm />,
    title: FEEDBACK_TITLE,
  };

  constructor(props) {
    super(props);

    this.state = {
      isOpen: false,
      content: this.props.content,
      feedbackType: FeedbackType.Rating,
    };
  }

  toggle = () => {
    this.setState({ isOpen: !this.state.isOpen });
  }

  changeType = (type: FeedbackType) => (e) =>  {
    let content;
    if (type === FeedbackType.Request) {
      content = <RequestFeedbackForm />;
    } else if (type === FeedbackType.Bug) {
      content = <BugReportFeedbackForm />;
    } else {
      content = <RatingFeedbackForm />;
    }
    this.setState({
      content,
      feedbackType: type,
    });
  };

  render() {
    return (
        <>
          <button className={`btn btn-flat-icon feedback-icon${this.state.isOpen ? ' is-open' : ''}`} onClick={this.toggle}>
            <img className='icon icon-help'/>
          </button>
          {
            this.state.isOpen &&
            <div className="feedback-component">
              <div className="feedback-header">
                <h3 className="title">
                  {this.props.title}
                </h3>
                <button type="button" className="btn btn-close" aria-label={BUTTON_CLOSE_TEXT} onClick={this.toggle} />
              </div>
              <div className="text-center">
                <div className="btn-group" role="group" aria-label={FEEDBACK_TYPE_TEXT}>
                  <button type="button"
                          className={"btn btn-default" + (this.state.feedbackType === FeedbackType.Rating? " active": "")}
                          onClick={this.changeType(FeedbackType.Rating)}>
                    {RATING_TEXT}
                  </button>
                  <button type="button"
                          className={"btn btn-default" + (this.state.feedbackType === FeedbackType.Bug? " active": "")}
                          onClick={this.changeType(FeedbackType.Bug)}>
                    {BUG_REPORT_TEXT}
                  </button>
                  <button type="button"
                          className={"btn btn-default" + (this.state.feedbackType === FeedbackType.Request? " active": "")}
                          onClick={this.changeType(FeedbackType.Request)}>
                    {REQUEST_TEXT}
                  </button>
                </div>
              </div>
              {this.state.content}
            </div>
          }
      </>
    );
  }
}
