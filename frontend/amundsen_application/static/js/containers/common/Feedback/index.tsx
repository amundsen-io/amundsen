import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from "../../../ducks/rootReducer";
import { submitFeedback, resetFeedback } from '../../../ducks/feedback/reducer';

import {
  RequestFeedbackForm,
  BugReportFeedbackForm,
  RatingFeedbackForm,
  DispatchFromProps,
  StateFromProps } from '../../../components/common/Feedback/FeedbackForm';

export const mapStateToProps = (state: GlobalState) => {
  return {
    sendState: state.feedback.sendState,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ submitFeedback, resetFeedback } , dispatch);
};

export const RatingFeedbackContainer =
  connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(RatingFeedbackForm);
export const BugReportFeedbackContainer =
  connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(BugReportFeedbackForm);
export const RequestFeedbackContainer =
  connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(RequestFeedbackForm);
