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
  COMMENTS_PLACEHOLDER,
  COMMENTS_MAX_LENGTH,
  COMMENTS_ROWS,
  RATING_VALUES,
  RATING_LABEL,
  RATING_LOW_TEXT,
  RATING_HIGH_TEXT,
  SUBMIT_TEXT,
} from '../../constants';

export class RatingFeedbackForm extends AbstractFeedbackForm {
  handleSubmit() {
    logAction({
      target_id: '',
      command: 'click',
      target_type: 'button',
      label: 'Submit Rating',
    });
  }

  renderCustom() {
    const radioButtonSet = RATING_VALUES.map((rating) => (
      <div className="radio-set-item" key={`value${rating}:item`}>
        <input
          type="radio"
          id={`value${rating}:input`}
          name="rating"
          value={`${rating}`}
        />
        <label
          id={`value${rating}:label`}
          htmlFor={`value${rating}:input`}
          className="text-title-w3"
        >
          {rating}
        </label>
      </div>
    ));

    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={this.submitForm}>
        <input type="hidden" name="feedback-type" value="NPS Rating" />
        <div className="form-group clearfix">
          <span className="text-title-w3">{RATING_LABEL}</span>
          <div>
            <div className="radio-set">{radioButtonSet}</div>
            <div>
              <span className="nps-label pull-left text-left text-title-w3">
                {RATING_LOW_TEXT}
              </span>
              <span className="nps-label pull-right text-right text-title-w3">
                {RATING_HIGH_TEXT}
              </span>
            </div>
          </div>
        </div>
        <div className="form-group">
          <label className="text-title-w3" htmlFor="comment">
            {COMMENTS_PLACEHOLDER}
          </label>
          <textarea
            className="form-control form-group"
            name="comment"
            id="comment"
            form={AbstractFeedbackForm.FORM_ID}
            rows={COMMENTS_ROWS}
            maxLength={COMMENTS_MAX_LENGTH}
            placeholder={COMMENTS_PLACEHOLDER}
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
)(RatingFeedbackForm);
