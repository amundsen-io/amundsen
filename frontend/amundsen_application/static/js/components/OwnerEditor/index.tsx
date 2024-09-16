// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';
import { Modal, OverlayTrigger, Popover } from 'react-bootstrap';

import AvatarLabel, { AvatarLabelProps } from 'components/AvatarLabel';

import LoadingSpinner from 'components/LoadingSpinner';
import { ResourceType, UpdateMethod, UpdateOwnerPayload } from 'interfaces';
import { logClick, logAction } from 'utils/analytics';
import { getUserIdLabel, getOwnersSectionConfig } from 'config/config-utils';

import { EditableSectionChildProps } from 'components/EditableSection';

import * as Constants from './constants';

import './styles.scss';
import InfoButton from 'components/InfoButton';

export interface DispatchFromProps {
  onUpdateList: (
    updateArray: UpdateOwnerPayload[],
    onSuccess?: () => any,
    onFailure?: () => any
  ) => void;
}

export interface ComponentProps {
  errorText?: string | null;
  resourceType: ResourceType;
}

interface OwnerAvatarLabelProps extends AvatarLabelProps {
  link?: string;
  isExternal?: boolean;
  additionalOwnerInfo?: any; // TODO should ownerCategory be a separate field? So we don't require OSS users to know the right key to use within additionalOwnerInfo?
}

export interface StateFromProps {
  isLoading: boolean;
  itemProps: OwnerItemProps;
}

export type OwnerEditorProps = ComponentProps &
  DispatchFromProps &
  StateFromProps &
  EditableSectionChildProps;

export type OwnerItemProps = { [id: string]: OwnerAvatarLabelProps };

interface OwnerEditorState {
  errorText: string | null;
  itemProps: OwnerItemProps;
  tempItemProps: { [id: string]: AvatarLabelProps };
}

export class OwnerEditor extends React.Component<
  OwnerEditorProps,
  OwnerEditorState
> {
  private inputRef: React.RefObject<HTMLInputElement>;

  public static defaultProps: Partial<OwnerEditorProps> = {
    errorText: null,
    isLoading: false,
    itemProps: {},
    onUpdateList: () => undefined,
  };

  constructor(props: OwnerEditorProps) {
    super(props);

    this.state = {
      errorText: props.errorText || null,
      itemProps: props.itemProps,
      tempItemProps: props.itemProps,
    };

    this.inputRef = React.createRef();
  }

  componentDidUpdate(prevProps) {
    const { itemProps } = this.props;

    // TODO - itemProps is a new object and this check needs to be fixed
    if (prevProps.itemProps !== itemProps) {
      this.setState({
        itemProps,
        tempItemProps: itemProps,
      });
    }
  }

  handleShow = () => {
    const { setEditMode } = this.props;

    if (setEditMode) {
      setEditMode(true);
    }
  };

  handleCancelEdit = () => {
    const { setEditMode } = this.props;
    const { itemProps } = this.state;

    this.setState({ tempItemProps: itemProps });
    if (setEditMode) {
      setEditMode(false);
    }
    logAction({
      command: 'click',
      target_id: 'cancel-owner-edit',
      label: 'Cancel Owner Edit',
    });
  };

  handleSaveEdit = () => {
    const { itemProps, tempItemProps } = this.state;
    const { setEditMode, onUpdateList } = this.props;

    const updateArray: UpdateOwnerPayload[] = [];

    Object.keys(itemProps).forEach((key) => {
      if (!tempItemProps.hasOwnProperty(key)) {
        updateArray.push({ method: UpdateMethod.DELETE, id: key });
      }
    });
    Object.keys(tempItemProps).forEach((key) => {
      if (!itemProps.hasOwnProperty(key)) {
        updateArray.push({ method: UpdateMethod.PUT, id: key });
      }
    });

    const onSuccessCallback = () => {
      if (setEditMode) {
        setEditMode(false);
      }
    };
    const onFailureCallback = () => {
      this.setState({
        errorText: Constants.DEFAULT_ERROR_TEXT,
      });
      if (setEditMode) {
        setEditMode(false);
      }
    };

    onUpdateList(updateArray, onSuccessCallback, onFailureCallback);
    logAction({
      command: 'click',
      target_id: 'save-owner-edit',
      label: 'Save Owner Edit',
    });
  };

  handleRecordAddItem = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const { tempItemProps } = this.state;

    if (this.inputRef.current) {
      const { value } = this.inputRef.current;

      if (value) {
        this.inputRef.current.value = '';

        const newTempItemProps = {
          ...tempItemProps,
          [value]: { label: value },
        };

        this.setState({ tempItemProps: newTempItemProps });
        logAction({
          command: 'click',
          target_id: 'add-owner-email',
          label: 'Add Owner Email',
          target_type: 'button',
        });
      }
    }
  };

  recordDeleteItem = (deletedKey: string) => {
    const { tempItemProps } = this.state;

    const newTempItemProps = Object.keys(tempItemProps)
      .filter((key) => key !== deletedKey)
      .reduce((obj, key) => ({ ...obj, [key]: tempItemProps[key] }), {});

    this.setState({ tempItemProps: newTempItemProps });
  };

  renderModalBody = () => {
    const { isEditing, isLoading } = this.props;
    const { tempItemProps } = this.state;

    if (!isEditing) {
      return null;
    }

    if (isLoading) {
      return (
        <Modal.Body>
          <LoadingSpinner />
        </Modal.Body>
      );
    }

    return (
      <Modal.Body>
        <form className="component-form" onSubmit={this.handleRecordAddItem}>
          {/* eslint-disable jsx-a11y/no-autofocus */}
          <input
            id="add-item-input"
            autoFocus
            placeholder={`Please enter ${getUserIdLabel()}`}
            ref={this.inputRef}
          />
          {/* eslint-enable jsx-a11y/no-autofocus */}
          <button className="btn btn-default add-button" type="submit">
            {Constants.ADD_ITEM}
          </button>
        </form>
        <ul className="component-list">
          {Object.keys(tempItemProps).map((key) => (
            <li key={`modal-list-item:${key}`}>
              {React.createElement(AvatarLabel, tempItemProps[key])}
              <button
                className="btn btn-flat-icon delete-button"
                onClick={() => this.recordDeleteItem(key)}
                type="button"
              >
                <span className="sr-only">{Constants.DELETE_ITEM}</span>
                <img className="icon icon-delete" alt="" />
              </button>
            </li>
          ))}
        </ul>
      </Modal.Body>
    );
  };

  renderOwnersList = () => {
    const { resourceType } = this.props;
    const { itemProps } = this.state;

    // TODO reuse the existing code for rendering each owner, refactor to a shareable method/function

    // Render owner list grouped by category, if categories configured
    if (getOwnersSectionConfig().categories.length > 0) {
      const sections = getOwnersSectionConfig().categories;

      console.log(`itemProps: ${JSON.stringify(itemProps)}`);

      console.log(`sections: ${JSON.stringify(sections)}`);

      // TODO confirm an owner added via UI edit button (i) adds immediately to the owners list without page refresh
      // (that's current behavior) and (ii) is added as "configured" in Lyft's Amundsen

      // TODO confirm when the config is not provided, keeps prior behavior

      return (
        <div>
          {sections.map((section, index) => (
            <ul className="component-list" key={index}>
              <span>{section.label}</span>
              <InfoButton infoText={section.definition} />

              {Object.keys(itemProps).map((key) => {
                const owner = itemProps[key];
                const avatarLabel = React.createElement(AvatarLabel, owner);

                console.log(`${JSON.stringify(owner)}`);

                let listItem: React.ReactNode;

                if (owner.link === undefined) {
                  listItem = avatarLabel;
                } else if (owner.isExternal) {
                  listItem = (
                    <a
                      href={owner.link}
                      target="_blank"
                      id={`${resourceType}-owners:${key}`}
                      data-type={`${resourceType}-owners`}
                      onClick={logClick}
                      rel="noopener noreferrer"
                    >
                      {avatarLabel}
                    </a>
                  );
                } else if (
                  section.label.toLowerCase() ===
                  owner.additionalOwnerInfo.owner_category.toLowerCase()
                ) {
                  listItem = (
                    <Link
                      to={owner.link}
                      id={`${resourceType}-owners:${key}`}
                      data-type={`${resourceType}-owners`}
                      onClick={logClick}
                    >
                      {avatarLabel}
                    </Link>
                  );
                }
                return <li key={`list-item:${key}`}>{listItem}</li>;
              })}
            </ul>
          ))}
        </div>
      );
    }

    // Render default owner list
    return (
      <ul className="component-list">
        {Object.keys(itemProps).map((key) => {
          const owner = itemProps[key];
          const avatarLabel = React.createElement(AvatarLabel, owner);

          console.log(`${JSON.stringify(owner)}`);

          let listItem: React.ReactNode;

          if (owner.link === undefined) {
            listItem = avatarLabel;
          } else if (owner.isExternal) {
            listItem = (
              <a
                href={owner.link}
                target="_blank"
                id={`${resourceType}-owners:${key}`}
                data-type={`${resourceType}-owners`}
                onClick={logClick}
                rel="noopener noreferrer"
              >
                {avatarLabel}
              </a>
            );
          } else {
            listItem = (
              <Link
                to={owner.link}
                id={`${resourceType}-owners:${key}`}
                data-type={`${resourceType}-owners`}
                onClick={logClick}
              >
                {avatarLabel}
              </Link>
            );
          }
          return <li key={`list-item:${key}`}>{listItem}</li>;
        })}
      </ul>
    );
  };

  render() {
    const { isEditing, readOnly, resourceType } = this.props;
    const { errorText, itemProps } = this.state;
    const hasItems = Object.keys(itemProps).length > 0;

    if (errorText) {
      return (
        <div className="owner-editor-component">
          <span className="status-message">{errorText}</span>
        </div>
      );
    }

    // TODO if popover works, refactor to put it on external owner too, DRY
    // TODO overlay is triggering when no text
    // TODO don't render the info button if no ownership context info available? There should always be context
    // for lyft owners though, we always have e.g. the update time

    const ownerList = hasItems ? this.renderOwnersList() : null;

    return (
      <div className="owner-editor-component">
        {ownerList}
        {readOnly && !hasItems && (
          <AvatarLabel
            avatarClass="gray-avatar"
            labelClass="text-placeholder"
            label={Constants.NO_OWNER_TEXT}
          />
        )}
        {!readOnly && !hasItems && (
          <button
            type="button"
            className="btn btn-flat-icon add-item-button"
            onClick={this.handleShow}
          >
            <img className="icon icon-plus-circle" alt="" />
            <span>{Constants.ADD_OWNER}</span>
          </button>
        )}
        {!readOnly && (
          <Modal
            className="owner-editor-modal"
            show={isEditing}
            onHide={this.handleCancelEdit}
          >
            <Modal.Header className="text-center" closeButton={false}>
              <Modal.Title>{Constants.OWNED_BY}</Modal.Title>
            </Modal.Header>
            {this.renderModalBody()}
            <Modal.Footer>
              <button
                type="button"
                className="btn btn-default"
                onClick={this.handleCancelEdit}
              >
                {Constants.CANCEL_TEXT}
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={this.handleSaveEdit}
              >
                {Constants.SAVE_TEXT}
              </button>
            </Modal.Footer>
          </Modal>
        )}
      </div>
    );
  }
}

export default OwnerEditor;
