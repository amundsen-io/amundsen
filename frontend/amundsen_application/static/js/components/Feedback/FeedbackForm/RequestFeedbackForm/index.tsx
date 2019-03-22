import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import AbstractFeedbackForm, { DispatchFromProps, StateFromProps } from '../../FeedbackForm';

import { GlobalState } from "../../../../ducks/rootReducer";
import { submitFeedback, resetFeedback } from '../../../../ducks/feedback/reducer';


export class RequestFeedbackForm extends AbstractFeedbackForm {
  constructor(props) {
    super(props)
  }

  renderCustom() {
    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={ this.submitForm }>
        <input type="hidden" name="feedback-type" value="Feature Request"/>
        <div className="form-group">
          <label>Feature Summary</label>
          <textarea name="feature-summary" className="form-control" rows={3} required={ true }
                    maxLength={ 2000 } placeholder="What feature are you requesting?"/>
        </div>
        <div className="form-group">
          <label>Value Proposition</label>
          <textarea name="value-prop" className="form-control" rows={5} required={ true }
                    maxLength={ 2000 } placeholder="How does this feature add value?"/>
        </div>
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

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(RequestFeedbackForm);
