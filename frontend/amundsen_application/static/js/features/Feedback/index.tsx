// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { Chat } from 'components/SVGIcons';
import { logAction } from 'utils/analytics';

import BugReportFeedbackForm from './FeedbackForm/BugReportFeedbackForm';
import RatingFeedbackForm from './FeedbackForm/RatingFeedbackForm';
import RequestFeedbackForm from './FeedbackForm/RequestFeedbackForm';

import * as Constants from './constants';

import './styles.scss';

const COLOR_LIGHT = '#ffffff';
const COLOR_DARK = '#292936'; // gray100

export interface FeedbackProps {
  content?: React.FC<any>;
  title?: string;
  theme: 'dark' | 'light';
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

  constructor(props: FeedbackProps) {
    super(props);
    const { content } = this.props;

    this.state = {
      isOpen: false,
      content,
      feedbackType: FeedbackType.Rating,
    };
  }

  toggle = () => {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'Toggle Feedback',
    });
    this.setState(({ isOpen }) => ({ isOpen: !isOpen }));
  };

  changeType = (type: FeedbackType) => () => {
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
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: `Feedback mode changed to ${type}`,
    });
  };

  render() {
    const { isOpen, feedbackType, content } = this.state;
    const { title, theme } = this.props;

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
          <Chat fill={theme === 'light' ? COLOR_LIGHT : COLOR_DARK} />
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
