import * as React from 'react';
import LoadingSpinner from '../../LoadingSpinner';

// TODO: Use css-modules instead of 'import'
import './styles.scss';
import { ResetFeedbackRequest, SubmitFeedbackRequest } from "../../../../ducks/feedback/types";

import { SendingState } from '../types';

interface FeedbackFormState {
  sendState: SendingState;
}

export interface StateFromProps {
  sendState: SendingState;
}

export interface DispatchFromProps {
  submitFeedback: (data: FormData) => SubmitFeedbackRequest;
  resetFeedback: () => ResetFeedbackRequest;
}

type FeedbackFormProps = StateFromProps & DispatchFromProps;

abstract class AbstractFeedbackForm extends React.Component<FeedbackFormProps, FeedbackFormState> {
  public static defaultProps: FeedbackFormProps = {
    sendState: SendingState.IDLE,
    submitFeedback: () => undefined,
    resetFeedback: () => undefined,
  };

  static FORM_ID = "feedback-form";

  protected constructor(props) {
    super(props);

    this.state = {
      sendState: this.props.sendState
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const { sendState } = nextProps;
    return { sendState };
  }

  submitForm = (event) => {
    event.preventDefault();
    const form = document.getElementById(AbstractFeedbackForm.FORM_ID) as HTMLFormElement;
    const formData = new FormData(form);
    this.props.submitFeedback(formData);
  };

  render() {
    if (this.state.sendState === SendingState.WAITING) {
      return <LoadingSpinner/>;
    }
    if (this.state.sendState === SendingState.COMPLETE) {
      return (
        <div className="success-message">
          Your feedback has been successfully submitted
        </div>
      );
    }
    return this.renderCustom();
  }

  abstract renderCustom();
}


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
          <button className="btn btn-light submit" type="submit">Submit</button>
        </div>
      </form>
    );
  }
}

export class BugReportFeedbackForm extends AbstractFeedbackForm {
  constructor(props) {
    super(props)
  }

  renderCustom() {
    return (
      <form id={AbstractFeedbackForm.FORM_ID} onSubmit={ this.submitForm }>
        <input type="hidden" name="feedback-type" value="Bug Report"/>
        <div className="form-group">
          <label>Bug Summary</label>
          <textarea name="bug-summary" className="form-control" required={ true }
                    rows={3} maxLength={ 2000 } placeholder="What went wrong?"/>
        </div>
        <div className="form-group">
          <label>Reproduction Steps</label>
          <textarea name="repro-steps" className="form-control" rows={5} required={ true }
                    maxLength={ 2000 } placeholder="What you did to encounter this bug?"/>
        </div>
        <div>
          <button className="btn btn-light submit" type="submit">Submit</button>
        </div>
      </form>
    );
  }
}

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
          <button className="btn btn-light submit" type="submit">Submit</button>
        </div>
      </form>
    );
  }
}

export default AbstractFeedbackForm;
