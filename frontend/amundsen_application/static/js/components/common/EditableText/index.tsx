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

export type EditableTextProps = ComponentProps & DispatchFromProps & StateFromProps;

interface EditableTextState {
  editable: boolean;
  inEditMode: boolean;
  value?: string;
  refreshValue?: string;
  isDisabled: boolean;
}

class EditableText extends React.Component<EditableTextProps, EditableTextState> {
  private textAreaTarget: HTMLTextAreaElement;
  private editAnchorTarget: HTMLAnchorElement;

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
  };

  enterEditMode = () => {
    if (this.props.getLatestValue) {
      const onSuccessCallback = () => { this.setState({ inEditMode: true }); };
      this.props.getLatestValue(onSuccessCallback, null);
    } else {
      this.setState({ inEditMode: true });
    }
  };

  refreshText = () => {
    this.setState({value: this.state.refreshValue, isDisabled: false, inEditMode: false, refreshValue: undefined });
  };

  updateText = () => {
    const newValue = ReactDOM.findDOMNode(this.textAreaTarget).value;
    const onSuccessCallback = () => { this.setState({value: newValue, inEditMode: false, refreshValue: undefined }); };
    const onFailureCallback = () => { this.exitEditMode(); };

    this.props.onSubmitValue(newValue, onSuccessCallback, onFailureCallback);
  };

  getTarget(type) {
    if (type === 'editAnchor') {
      return ReactDOM.findDOMNode(this.editAnchorTarget);
    }
    if (type === 'textArea') {
      return ReactDOM.findDOMNode(this.textAreaTarget)
    }
  }

  render() {
    if (!this.state.editable) {
      return (
        <div id='editable-container' className='editable-container'>
           <div id='editable-text' className='editable-text'>{ this.state.value }</div>
        </div>
      );
    }
    if (!this.state.inEditMode || (this.state.inEditMode && this.state.isDisabled)) {
      return (
        <div id='editable-container' className='editable-container'>
          <Overlay
            placement='top'
            show={this.state.isDisabled}
            target={this.getTarget.bind(this,'editAnchor')}
          >
            <Tooltip id='error-tooltip'>
              <div className="error-tooltip">
                <text>This text is out of date, please refresh the component</text>
                <button onClick={this.refreshText} className="btn btn-flat-icon">
                  <img className='icon icon-refresh'/>
                </button>
              </div>
            </Tooltip>
          </Overlay>
          <div id='editable-text' className={"editable-text"}>
            { this.state.value }
            <a className={ "edit-link" + (this.state.value ? "" : " no-value") }
               href="JavaScript:void(0)"
               onClick={ this.enterEditMode }
               ref={ anchor => {
                  this.editAnchorTarget = anchor;
                }}
            >
              {
                this.state.value ? "edit" : "Add Description"
              }
            </a>
          </div>
        </div>
      );
    }

    return (
      <div id='editable-container' className='editable-container'>
        <textarea
          id='editable-textarea'
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
