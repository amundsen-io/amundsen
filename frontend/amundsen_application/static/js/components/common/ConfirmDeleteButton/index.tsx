import * as React from 'react';
import ReactDOM from 'react-dom';
import { Overlay, Popover } from 'react-bootstrap';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

interface ConfirmDeleteButtonProps {
  onConfirmHandler: (event: React.SyntheticEvent<any>) => any;
  popoverTitle?: string;
}

interface ConfirmDeleteButtonState {
  showPopover: boolean;
}

class ConfirmDeleteButton extends React.Component<ConfirmDeleteButtonProps, ConfirmDeleteButtonState> {
  private buttonRef: React.RefObject<HTMLButtonElement>;

  public static defaultProps: ConfirmDeleteButtonProps = {
    onConfirmHandler: () => {},
    popoverTitle: 'Confirm Delete?',
  };

  constructor(props) {
    super(props);
    this.state = {
      showPopover: false,
    }

    this.buttonRef = React.createRef();

    this.cancelDelete = this.cancelDelete.bind(this);
    this.confirmDelete = this.confirmDelete.bind(this);
    this.triggerPopup = this.triggerPopup.bind(this);

    this.getTarget = this.getTarget.bind(this);
  }

  cancelDelete() {
    this.setState({showPopover: false});
  }

  confirmDelete(event) {
    this.props.onConfirmHandler(event);
    this.setState({showPopover: false});
  }

  triggerPopup() {
    this.setState({showPopover: true});
  }

  getTarget() {
    return ReactDOM.findDOMNode(this.buttonRef.current);
  }

  render() {
    /*
      TODO Internationalization: need confirm/delete icons to replace "Yes/No"
      in order to minimize harcoded English text
      TODO Accessibility: The popover interaction will need to be revisited for
      accesibility, interactive content currently cannot be reached via keyboard.
      https://reactjs.org/docs/accessibility.html
    */
    return (
      <div className='confirm-delete-button'>
        <button
          className='delete-button'
          aria-label='delete'
          onClick={this.triggerPopup}
          ref={this.buttonRef}
        >
          <span aria-hidden='true'>&times;</span>
        </button>

        <Overlay
          placement='top'
          show={this.state.showPopover}
          target={this.getTarget}
        >
          <Popover title={this.props.popoverTitle}>
            <button aria-label='cancel' onClick={this.confirmDelete}>Yes</button>
            <button aria-label='confirm' onClick={this.cancelDelete}>No</button>
          </Popover>
        </Overlay>
      </div>
    );
  }

}

export default ConfirmDeleteButton;
