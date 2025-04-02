// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { GlobalState } from 'ducks/rootReducer';
import { submitFeedback, resetFeedback } from 'ducks/feedback/reducer';
import { logAction } from 'utils/analytics';

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
  handleSubmit() {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'Submit Feature Request',
    });
  }

  renderCustom() {
    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={this.submitForm}>
        <input type="hidden" name="feedback-type" value="Feature Request" />
        <div className="form-group">
          <label className="text-title-w3" htmlFor="subject">
            {SUBJECT_LABEL}
          </label>
          <input
            type="text"
            autoComplete="off"
            id="subject"
            name="subject"
            className="form-control"
            required
            placeholder={SUBJECT_PLACEHOLDER}
          />
        </div>
        <div className="form-group">
          <label className="text-title-w3" htmlFor="feature-summary">
            {FEATURE_SUMMARY_LABEL}
          </label>
          <textarea
            id="feature-summary"
            name="feature-summary"
            className="form-control"
            rows={3}
            required
            maxLength={2000}
            placeholder={FEATURE_SUMMARY_PLACEHOLDER}
          />
        </div>
        <div className="form-group">
          <label className="text-title-w3" htmlFor="value-prop">
            {PROPOSITION_LABEL}
          </label>
          <textarea
            id="value-prop"
            name="value-prop"
            className="form-control"
            rows={5}
            required
            maxLength={2000}
            placeholder={PROPOSITION_PLACEHOLDER}
          />
        </div>
        <button
          className="btn btn-primary"
          type="submit"
          onClick={this.handleSubmit}
        >
          {SUBMIT_TEXT}
        </button>
      </form>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => ({
  sendState: state.feedback.sendState,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ submitFeedback, resetFeedback }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(RequestFeedbackForm);
