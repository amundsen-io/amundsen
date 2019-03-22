import * as React from 'react';
import LoadingSpinner from '../../common/LoadingSpinner';

// TODO: Use css-modules instead of 'import'
import './styles.scss';
import { ResetFeedbackRequest, SubmitFeedbackRequest } from "../../../ducks/feedback/types";

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

export default AbstractFeedbackForm;
