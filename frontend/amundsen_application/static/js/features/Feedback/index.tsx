// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { Chat } from 'components/SVGIcons';
import BugReportFeedbackForm from './FeedbackForm/BugReportFeedbackForm';
import RatingFeedbackForm from './FeedbackForm/RatingFeedbackForm';
import RequestFeedbackForm from './FeedbackForm/RequestFeedbackForm';

import * as Constants from './constants';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

const COLOR_WHITE = '#ffffff';

export interface FeedbackProps {
  content?: React.FC<any>;
  title?: string;
}

interface FeedbackState {
  content?: React.FC<any>;
  feedbackType: FeedbackType;
  isOpen: boolean;
}

export enum FeedbackType {
  Rating,
  Bug,
  Request,
}

export default class Feedback extends React.Component<
  FeedbackProps,
  FeedbackState
> {
  static defaultProps = {
    content: <RatingFeedbackForm />,
    title: Constants.FEEDBACK_TITLE,
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
  };

  changeType = (type: FeedbackType) => (e) => {
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
    const { isOpen, feedbackType, content } = this.state;
    const { title } = this.props;

    return (
      <>
        <button
          className={`btn btn-flat-icon btn-nav-bar-icon${
            isOpen ? ' is-open' : ''
          }`}
          onClick={this.toggle}
          type="button"
        >
          <span className="sr-only">{Constants.FEEDBACK_BUTTON_TEXT}</span>
          <Chat fill={COLOR_WHITE} />
        </button>
        {isOpen && (
          <div className="feedback-component">
            <div className="feedback-header">
              <h3 className="title">{title}</h3>
              <button
                type="button"
                className="btn btn-close"
                onClick={this.toggle}
              >
                <span className="sr-only">{Constants.BUTTON_CLOSE_TEXT}</span>
              </button>
            </div>
            <div className="text-center">
              <div className="btn-group" role="group">
                <span className="sr-only">{Constants.FEEDBACK_TYPE_TEXT}</span>
                <button
                  type="button"
                  className={
                    'btn btn-default' +
                    (feedbackType === FeedbackType.Rating ? ' active' : '')
                  }
                  onClick={this.changeType(FeedbackType.Rating)}
                >
                  {Constants.RATING_TEXT}
                </button>
                <button
                  type="button"
                  className={
                    'btn btn-default' +
                    (feedbackType === FeedbackType.Bug ? ' active' : '')
                  }
                  onClick={this.changeType(FeedbackType.Bug)}
                >
                  {Constants.BUG_REPORT_TEXT}
                </button>
                <button
                  type="button"
                  className={
                    'btn btn-default' +
                    (feedbackType === FeedbackType.Request ? ' active' : '')
                  }
                  onClick={this.changeType(FeedbackType.Request)}
                >
                  {Constants.REQUEST_TEXT}
                </button>
              </div>
            </div>
            {content}
          </div>
        )}
      </>
    );
  }
}
