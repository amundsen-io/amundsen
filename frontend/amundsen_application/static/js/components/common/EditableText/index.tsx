import * as React from 'react';
import ReactDOM from 'react-dom';
import { Overlay, Popover, Tooltip } from 'react-bootstrap';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

export interface StateFromProps {
  refreshValue?: string;
}

export interface DispatchFromProps {
  getLatestValue?: (onSuccess?: () => any, onFailure?: () => any) => void;
  onSubmitValue: (newValue: string, onSuccess?: () => any, onFailure?: () => any) => void;
}

export interface ComponentProps {
  editable?: boolean;
  maxLength?: number;
  value?: string;
}

type EditableTextProps = ComponentProps & DispatchFromProps & StateFromProps;

interface EditableTextState {
  editable: boolean;
  inEditMode: boolean;
  value?: string;
  refreshValue?: string;
  isDisabled: boolean;
}

class EditableText extends React.Component<EditableTextProps, EditableTextState> {
  private textAreaTarget: HTMLTextAreaElement;
  private editButtonTarget: HTMLButtonElement;

  public static defaultProps: EditableTextProps = {
    editable: true,
    maxLength: 250,
    onSubmitValue: null,
    getLatestValue: null,
    value: '',
  };

  static getDerivedStateFromProps(nextProps, prevState) {
    const { refreshValue } = nextProps;
    return { refreshValue };
  }

  constructor(props) {
    super(props);
    this.state = {
      editable: props.editable,
      inEditMode: false,
      isDisabled: false,
      value: props.value,
      refreshValue: props.value,
    };
  }

  componentDidUpdate() {
    const { isDisabled, inEditMode, refreshValue, value } = this.state;
    if (inEditMode) {
      if (refreshValue && refreshValue !== value && !isDisabled) {
        // disable the component if a refresh is needed
        this.setState({ isDisabled: true })
      }
      else {
        // when entering edit mode, place focus in the textarea
        const textArea = ReactDOM.findDOMNode(this.textAreaTarget);
        if (textArea) {
          textArea.focus();
        }
      }
    }
  }

  exitEditMode = () => {
    this.setState({ isDisabled: false, inEditMode: false, refreshValue: '' });
  }

  enterEditMode = () => {
    if (this.props.getLatestValue) {
      const onSuccessCallback = () => { this.setState({ inEditMode: true }); };
      this.props.getLatestValue(onSuccessCallback, null);
    } else {
      this.setState({ inEditMode: true });
    }
  }

  refreshText = () => {
    this.setState({value: this.state.refreshValue, isDisabled: false, inEditMode: false, refreshValue: undefined });
  }

  updateText = () => {
    const newValue = ReactDOM.findDOMNode(this.textAreaTarget).value;
    const onSuccessCallback = () => { this.setState({value: newValue, inEditMode: false, refreshValue: undefined }); };
    const onFailureCallback = () => { this.exitEditMode(); }

    this.props.onSubmitValue(newValue, onSuccessCallback, onFailureCallback);
  }

  getTarget(type) {
    if (type === 'editButton') {
      return ReactDOM.findDOMNode(this.editButtonTarget);
    }
    if (type === 'textArea') {
      return ReactDOM.findDOMNode(this.textAreaTarget)
    }
  }

  render() {
    if (!this.state.inEditMode || (this.state.inEditMode && this.state.isDisabled)){
      return (
        <div className='editable-container'>
          {
            this.state.editable &&
            <div>
              <button
                className='btn icon edit-button'
                disabled= { this.state.isDisabled }
                onClick={ this.enterEditMode }
                ref={button => {
                  this.editButtonTarget = button;
                }}
              />
              <Overlay
                placement='top'
                show={this.state.isDisabled}
                target={this.getTarget.bind(this,'editButton')}
              >
                <Tooltip id='error-tooltip'>
                  <div className="error-tooltip">
                    <text>This text is out of date, please refresh the component</text>
                    <button onClick={this.refreshText}>&#xe031;</button>
                  </div>
                </Tooltip>
              </Overlay>
            </div>
          }
          <div className='editable-text'>{ this.state.value }</div>
        </div>
      );
    }

    return (
      <div className='editable-container'>
        <textarea
          id='textAreaInput'
          className='editable-textarea'
          rows={2}
          maxLength={this.props.maxLength}
          ref={textarea => {
            this.textAreaTarget = textarea;
          }}
        >
          {this.state.value}
        </textarea>

        <Overlay
          placement='top'
          show={true}
          target={this.getTarget.bind(this,'textArea')}
        >
          <Tooltip>
            <button id='cancel' onClick={this.exitEditMode}>Cancel</button>
            <button id='save' onClick={this.updateText}>Save</button>
          </Tooltip>
        </Overlay>

      </div>
    );
  }
}

export default EditableText;
