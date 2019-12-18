import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { Link } from 'react-router-dom';

import AppConfig from 'config/config';
import AvatarLabel, { AvatarLabelProps } from 'components/common/AvatarLabel';
import LoadingSpinner from 'components/common/LoadingSpinner';
import { Modal } from 'react-bootstrap';
import { UpdateMethod, UpdateOwnerPayload } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

const DEFAULT_ERROR_TEXT = 'There was a problem with the request, please reload the page.';

import { GlobalState } from 'ducks/rootReducer';
import { updateTableOwner } from 'ducks/tableMetadata/owners/reducer';
import { EditableSectionChildProps } from 'components/TableDetail/EditableSection';
import { logClick } from 'ducks/utilMethods';

export interface DispatchFromProps {
  onUpdateList: (updateArray: UpdateOwnerPayload[], onSuccess?: () => any, onFailure?: () => any) => void;
}

export interface ComponentProps {
  errorText?: string | null;
}

interface OwnerAvatarLabelProps extends AvatarLabelProps {
  link?: string;
  isExternal?: boolean;
}

export interface StateFromProps {
  isLoading: boolean;
  itemProps: { [id: string]: OwnerAvatarLabelProps };
}

type OwnerEditorProps = ComponentProps & DispatchFromProps & StateFromProps & EditableSectionChildProps;

interface OwnerEditorState {
  errorText: string | null;
  itemProps: { [id: string]: OwnerAvatarLabelProps };
  readOnly: boolean;
  tempItemProps: { [id: string]: AvatarLabelProps };
}

export class OwnerEditor extends React.Component<OwnerEditorProps, OwnerEditorState> {
  private inputRef: React.RefObject<HTMLInputElement>;

  public static defaultProps: OwnerEditorProps = {
    errorText: null,
    isLoading: false,
    itemProps: {},
    onUpdateList: () => undefined,
  };

  constructor(props) {
    super(props);

    this.state = {
      errorText: props.errorText,
      itemProps: props.itemProps,
      readOnly: props.readOnly,
      tempItemProps: props.itemProps,
    };

    this.inputRef = React.createRef();
  }

  componentDidUpdate(prevProps) {
    // TODO - itemProps is a new object and this check needs to be fixed
    if (prevProps.itemProps !== this.props.itemProps) {
      this.setState({ itemProps: this.props.itemProps, tempItemProps: this.props.itemProps });
    }
  }

  handleShow = () => {
    this.props.setEditMode(true)
  };

  cancelEdit = () => {
    this.setState({ tempItemProps: this.state.itemProps });
    this.props.setEditMode(false);
  };

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
      this.props.setEditMode(false);
    };
    const onFailureCallback = () => {
      this.setState({ errorText: DEFAULT_ERROR_TEXT, readOnly: true });
      this.props.setEditMode(false);
    };
    this.props.onUpdateList(updateArray, onSuccessCallback, onFailureCallback);
  };

  recordAddItem = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const value = this.inputRef.current.value;
    if (value) {
      this.inputRef.current.value = '';
      const newTempItemProps = {
        ...this.state.tempItemProps,
        [value]: { label: value },
      };
      this.setState({ tempItemProps: newTempItemProps });
    }
  };

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
  };

  renderModalBody = () => {
    if (!this.props.isEditing) {
      return null;
    }

    if (this.props.isLoading) {
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
  };

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
              const owner = this.state.itemProps[key]
              const avatarLabel = React.createElement(AvatarLabel, owner)

              let listItem;
              if (owner.link === undefined) {
                listItem = avatarLabel
              } else if (owner.isExternal) {
                listItem =
                  <a href={owner.link} target="_blank" id={`table-owners:${key}`} onClick={logClick}>
                    { avatarLabel }
                  </a>
              } else {
                listItem =
                  <Link to={owner.link} id={`table-owners:${key}`} onClick={logClick}>
                    { avatarLabel }
                  </Link>
              }

              return (
                <li key={`list-item:${key}`}>
                  { listItem }
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
          !this.state.readOnly && Object.keys(this.state.itemProps).length === 0 &&
          <button
           className='btn btn-flat-icon add-item-button'
           onClick={ this.handleShow }>
             <img className='icon icon-plus-circle'/>
             <span>Add Owner</span>
          </button>
        }

        <Modal className='owner-editor-modal' show={ this.props.isEditing } onHide={ this.cancelEdit }>
          <Modal.Header className="text-center" closeButton={false}>
            <Modal.Title>Owned By</Modal.Title>
          </Modal.Header>
          { this.renderModalBody() }
          <Modal.Footer>
            <button type="button" className="btn btn-default" onClick={ this.cancelEdit }>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={ this.saveEdit }>Save</button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const ownerObj = state.tableMetadata.tableOwners.owners;
  const items = Object.keys(ownerObj).reduce((obj, ownerId) => {
    const { profile_url, user_id, display_name } = ownerObj[ownerId];
    let profileLink = profile_url;
    let isExternalLink = true;
    if (AppConfig.indexUsers.enabled) {
      isExternalLink = false;
      profileLink = `/user/${user_id}?source=owned_by`;
    }
    obj[ownerId] = { label: display_name, link: profileLink, isExternal: isExternalLink }
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
