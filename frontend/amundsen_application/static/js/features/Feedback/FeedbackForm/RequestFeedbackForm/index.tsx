// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import { submitFeedback, resetFeedback } from 'ducks/feedback/reducer';
import AbstractFeedbackForm, { DispatchFromProps, StateFromProps } from '..';

import {
  FEATURE_SUMMARY_LABEL,
  FEATURE_SUMMARY_PLACEHOLDER,
  PROPOSITION_LABEL,
  PROPOSITION_PLACEHOLDER,
  SUBJECT_LABEL,
  SUBJECT_PLACEHOLDER,
  SUBMIT_TEXT,
} from '../../constants';

export class RequestFeedbackForm extends AbstractFeedbackForm {
  renderCustom() {
    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={this.submitForm}>
        <input type="hidden" name="feedback-type" value="Feature Request" />
        <div className="form-group">
          <label>{SUBJECT_LABEL}</label>
          <input
            type="text"
            autoComplete="off"
            name="subject"
            className="form-control"
            required
            placeholder={SUBJECT_PLACEHOLDER}
          />
        </div>
        <div className="form-group">
          <label>{FEATURE_SUMMARY_LABEL}</label>
          <textarea
            name="feature-summary"
            className="form-control"
            rows={3}
            required
            maxLength={2000}
            placeholder={FEATURE_SUMMARY_PLACEHOLDER}
          />
        </div>
        <div className="form-group">
          <label>{PROPOSITION_LABEL}</label>
          <textarea
            name="value-prop"
            className="form-control"
            rows={5}
            required
            maxLength={2000}
            placeholder={PROPOSITION_PLACEHOLDER}
          />
        </div>
        <button className="btn btn-primary" type="submit">
          {SUBMIT_TEXT}
        </button>
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
  return bindActionCreators({ submitFeedback, resetFeedback }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(RequestFeedbackForm);
