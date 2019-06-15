import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import ReactDOM from 'react-dom';
import serialize from 'form-serialize';

import AvatarLabel, { AvatarLabelProps } from 'components/common/AvatarLabel';
import LoadingSpinner from 'components/common/LoadingSpinner';
import { Modal } from 'react-bootstrap';
import { UpdateMethod } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

const DEFAULT_ERROR_TEXT = 'There was a problem with the request, please reload the page.';

import { GlobalState } from 'ducks/rootReducer';
import { updateTableOwner } from 'ducks/tableMetadata/owners/reducer';

export interface DispatchFromProps {
  onUpdateList: (updateArray: { method: UpdateMethod; id: string; }[], onSuccess?: () => any, onFailure?: () => any) => void;
}

export interface ComponentProps {
  errorText?: string | null;
  readOnly: boolean;
}

export interface StateFromProps {
  isLoading: boolean;
  itemProps: { [id: string]: AvatarLabelProps };
}

type OwnerEditorProps = ComponentProps & DispatchFromProps & StateFromProps;

interface OwnerEditorState {
  errorText: string | null;
  isLoading: boolean;
  itemProps: { [id: string]: AvatarLabelProps };
  readOnly: boolean;
  showModal: boolean;
  tempItemProps: { [id: string]: AvatarLabelProps };
}

export class OwnerEditor extends React.Component<OwnerEditorProps, OwnerEditorState> {
  private inputRef: React.RefObject<HTMLInputElement>;

  public static defaultProps: OwnerEditorProps = {
    errorText: null,
    isLoading: false,
    itemProps: {},
    onUpdateList: () => undefined,
    readOnly: true,
  };

  static getDerivedStateFromProps(nextProps, prevState) {
    const { isLoading, itemProps, readOnly } = nextProps;
    return { isLoading, itemProps, readOnly, tempItemProps: itemProps };
  }

  constructor(props) {
    super(props);

    this.state = {
      errorText: props.errorText,
      isLoading: props.isLoading,
      itemProps: props.itemProps,
      readOnly: props.readOnly,
      showModal: false,
      tempItemProps: props.itemProps,
    };

    this.inputRef = React.createRef();
  }

  handleShow = () => {
    this.setState({ showModal: true });
  }

  cancelEdit = () => {
    this.setState({ tempItemProps: this.state.itemProps, showModal: false });
  }

  saveEdit = () => {
    const updateArray = [];
    Object.keys(this.state.itemProps).forEach((key) => {
      if (!this.state.tempItemProps.hasOwnProperty(key)) {
        updateArray.push({ method: UpdateMethod.DELETE, id: key });
      }
    });
    Object.keys(this.state.tempItemProps).forEach((key) => {
      if (!this.state.itemProps.hasOwnProperty(key)) {
        updateArray.push({ method: UpdateMethod.PUT, id: key });
      }
    });

    const onSuccessCallback = () => {
      this.setState({ showModal: false });
    }
    const onFailureCallback = () => {
      this.setState({ errorText: DEFAULT_ERROR_TEXT, readOnly: true, showModal: false });
    }
    this.props.onUpdateList(updateArray, onSuccessCallback, onFailureCallback);
  }

  recordAddItem = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const value = this.inputRef.current.value;
    if (value) {
      this.inputRef.current.value = '';
      const newTempItemProps = {
        ...this.state.tempItemProps,
        [value]: { label: value },
      }
      this.setState({ tempItemProps: newTempItemProps });
    }
  }

  recordDeleteItem = (deletedKey: string) => {
    const newTempItemProps = Object.keys(this.state.tempItemProps)
    .filter((key) => {
      return key !== deletedKey
    })
    .reduce((obj, key) => {
      obj[key] = this.state.tempItemProps[key];
      return obj;
    }, {});
    this.setState({ tempItemProps: newTempItemProps });
  }

  renderModalBody = () => {
    if (!this.state.showModal) {
      return null;
    }

    if (this.state.isLoading) {
      return (
        <Modal.Body>
          <LoadingSpinner/>
        </Modal.Body>
      )
    }

    return (
      <Modal.Body>
        <form className='component-form' onSubmit={this.recordAddItem}>
          <input
            id='add-item-input'
            autoFocus={true}
            placeholder='Enter an email address'
            ref={ this.inputRef }
          />
          <button className="btn btn-default add-button" type="submit" aria-label="Add Item">
            <span aria-hidden="true">Add</span>
          </button>
        </form>
        <ul className='component-list'>
          {
            Object.keys(this.state.tempItemProps).map((key) => {
              return (
                <li key={`modal-list-item:${key}`}>
                  { React.createElement(AvatarLabel, this.state.tempItemProps[key]) }
                  <button
                    className='btn btn-flat-icon delete-button'
                    aria-label='Delete Item'
                    /* tslint:disable - TODO: Investigate jsx-no-lambda rule */
                    onClick={() => this.recordDeleteItem(key)}
                    /* tslint:enable */
                  >
                   <img className='icon icon-delete'/>
                  </button>
                </li>
              );
            })
          }
        </ul>
      </Modal.Body>
    );
  }

  render() {
    let content;

    if (this.state.errorText) {
      return (
        <div className='owner-editor-component'>
          <label className="status-message">{this.state.errorText}</label>
        </div>
      );
    }

    if (this.state.itemProps.size === 0) {
      content = <label className="status-message">No entries exist</label>;
    }
    else {
      content = (
        <ul className='component-list'>
          {
            Object.keys(this.state.itemProps).map((key) => {
              return (
                <li key={`list-item:${key}`}>
                  { React.createElement(AvatarLabel, this.state.itemProps[key]) }
                </li>
              );
            })
          }
        </ul>
      );
    }

    return (
      <div className='owner-editor-component'>
        { content }
        {
          !this.state.readOnly &&
          <button
           className='btn btn-flat-icon add-item-button'
           onClick={this.handleShow}>
             <img className='icon icon-plus-circle'/>
             <span>Add</span>
          </button>
        }

        <Modal className='owner-editor-modal' show={this.state.showModal} onHide={this.cancelEdit}>
          <Modal.Header className="text-center" closeButton={false}>
            <Modal.Title>Owned By</Modal.Title>
          </Modal.Header>
          { this.renderModalBody() }
          <Modal.Footer>
            <button type="button" className="btn btn-default" onClick={this.cancelEdit}>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={this.saveEdit}>Save</button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const ownerObj = state.tableMetadata.tableOwners.owners;
  const items = Object.keys(ownerObj).reduce((obj, ownerId) => {
    obj[ownerId] = { label: ownerObj[ownerId].display_name }
    return obj;
  }, {});

  return {
    isLoading: state.tableMetadata.tableOwners.isLoading,
    itemProps: items,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ onUpdateList: updateTableOwner } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, ComponentProps>(mapStateToProps, mapDispatchToProps)(OwnerEditor);
