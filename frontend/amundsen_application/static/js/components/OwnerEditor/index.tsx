// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';
import { Modal } from 'react-bootstrap';

import AvatarLabel, { AvatarLabelProps } from 'components/AvatarLabel';
import LoadingSpinner from 'components/LoadingSpinner';
import { ResourceType, UpdateMethod, UpdateOwnerPayload } from 'interfaces';
import { logClick, logAction } from 'utils/analytics';
import { getUserIdLabel, getOwnersSectionConfig } from 'config/config-utils';

import { EditableSectionChildProps } from 'components/EditableSection';
import InfoButton from 'components/InfoButton';
import { OwnerCategory } from 'interfaces/OwnerCategory';

import * as Constants from './constants';

import './styles.scss';

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
  additionalOwnerInfo?: any;
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

  renderOwnersSection = (section: OwnerCategory | null) => {
    const { resourceType } = this.props;
    const { itemProps } = this.state;

    // check if rendering an owner category that lacks any entries
    let isEmptySection = false;

    if (section !== null) {
      isEmptySection = Object.keys(itemProps).every(
        (key) =>
          itemProps[key].additionalOwnerInfo.owner_category.toLowerCase() !==
          section?.label?.toLowerCase()
      );
    }

    return (
      <ul className="component-list">
        {section ? (
          <div>
            <span className="title-3">{section.label}</span>
            <InfoButton infoText={section.definition} />
          </div>
        ) : null}
        {isEmptySection ? <span className="body-3">None known</span> : null}

        {Object.keys(itemProps).map((key) => {
          const owner = itemProps[key];
          const avatarLabel = React.createElement(AvatarLabel, owner);

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
            (section && // if section, only render owner that matches category
              section.label.toLowerCase() ===
                owner.additionalOwnerInfo.owner_category.toLowerCase()) ||
            !section
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
    );
  };

  renderOwnersList = () => {
    const sections = getOwnersSectionConfig().categories;
    const { itemProps } = this.state;

    if (
      sections.length > 0 &&
      // render default way if there are any uncategorized owners
      Object.keys(itemProps).every((key) => {
        return itemProps[key].additionalOwnerInfo?.owner_category;
      })
    ) {
      return (
        <div>
          {sections.map((section) => this.renderOwnersSection(section))}
        </div>
      );
    }

    return this.renderOwnersSection(null);
  };

  render() {
    const { isEditing, readOnly } = this.props;
    const { errorText, itemProps } = this.state;
    const hasItems = Object.keys(itemProps).length > 0;

    if (errorText) {
      return (
        <div className="owner-editor-component">
          <span className="status-message">{errorText}</span>
        </div>
      );
    }

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
