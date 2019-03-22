import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import AbstractFeedbackForm, { DispatchFromProps, StateFromProps } from '../../FeedbackForm';

import { GlobalState } from "../../../../ducks/rootReducer";
import { submitFeedback, resetFeedback } from '../../../../ducks/feedback/reducer';

export class RatingFeedbackForm extends AbstractFeedbackForm {
  constructor(props) {
    super(props)
  }

  renderCustom() {
    const ratings = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const radioButtonSet = ratings.map(rating => (
      <div className="radio-set-item" key={`value${rating}:item`}>
        <input type="radio" id={`value${rating}:input`} name="rating" value={`${rating}`}/>
        <label id={`value${rating}:label`} htmlFor={`value${rating}:input`}>{rating}</label>
      </div>
    ));

    /* TODO: harcoded strings that should be translatable/customizable */
    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={ this.submitForm }>
        <input type="hidden" name="feedback-type" value="NPS Rating"/>
        <div>How likely are you to recommend this tool to a friend or co-worker?</div>
        <div className="radio-set">
          { radioButtonSet }
        </div>
        <div>
          <div className="nps-label pull-left text-left">Not Very Likely</div>
          <div className="nps-label pull-right text-right">Very Likely</div>
        </div>
        <textarea name="comment" form={AbstractFeedbackForm.FORM_ID}
          rows={ 5 } maxLength={ 2000 } placeholder="Additional Comments"/>
        <div>
          <button className="btn btn-default submit" type="submit">Submit</button>
        </div>
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

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(RatingFeedbackForm);
