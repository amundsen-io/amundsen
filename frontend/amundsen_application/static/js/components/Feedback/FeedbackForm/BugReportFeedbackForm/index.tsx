import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import AbstractFeedbackForm, { DispatchFromProps, StateFromProps } from '../../FeedbackForm';

import { GlobalState } from 'ducks/rootReducer';
import { submitFeedback, resetFeedback } from 'ducks/feedback/reducer';

import {
  BUG_SUMMARY_LABEL,
  BUG_SUMMARY_PLACEHOLDER,
  REPRO_STEPS_LABEL,
  REPRO_STEPS_PLACEHOLDER,
  SUBJECT_LABEL,
  SUBJECT_PLACEHOLDER,
  SUBMIT_TEXT,
} from '../../constants';

export class BugReportFeedbackForm extends AbstractFeedbackForm {
  constructor(props) {
    super(props);
  }

  renderCustom() {
    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={ this.submitForm }>
        <input type="hidden" name="feedback-type" value="Bug Report"/>
        <div className="form-group">
          <label>{SUBJECT_LABEL}</label>
          <input type="text" name="subject" className="form-control" required={ true } placeholder={SUBJECT_PLACEHOLDER} />
        </div>
        <div className="form-group">
          <label>{BUG_SUMMARY_LABEL}</label>
          <textarea name="bug-summary" className="form-control" required={ true }
                    rows={3} maxLength={ 2000 } placeholder={BUG_SUMMARY_PLACEHOLDER}/>
        </div>
        <div className="form-group">
          <label>{REPRO_STEPS_LABEL}</label>
          <textarea name="repro-steps" className="form-control" rows={5} required={ true }
                    maxLength={ 2000 } placeholder={REPRO_STEPS_PLACEHOLDER}/>
        </div>
        <button className="btn btn-primary" type="submit">{SUBMIT_TEXT}</button>
      </form>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    sendState: state.feedback.sendState,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ submitFeedback, resetFeedback } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(BugReportFeedbackForm);
