/* eslint-disable jsx-a11y/click-events-have-key-events */
// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { OverlayTrigger, Popover } from 'react-bootstrap';

import { logClick } from 'utils/analytics';

import * as Constants from './constants';

import './styles.scss';

export interface EditableSectionProps {
  title: string;
  readOnly?: boolean;
  /* Should be used when readOnly=true to prompt users with a relevant explanation for the given use case */
  editText?: string;
  /* Should be used when readOnly=true to link to the source where users can edit the given metadata */
  editUrl?: string;
}

interface EditableSectionState {
  isEditing: boolean;
}

export interface EditableSectionChildProps {
  isEditing?: boolean;
  setEditMode?: (isEditing: boolean) => void;
  readOnly?: boolean;
}

export class EditableSection extends React.Component<
  EditableSectionProps,
  EditableSectionState
> {
  static defaultProps: Partial<EditableSectionProps> = {
    editText: Constants.EDIT_TEXT,
  };

  static convertText(str: string): string {
    return str
      .split(new RegExp('[\\s+_]'))
      .map((x) => x.charAt(0).toUpperCase() + x.slice(1).toLowerCase())
      .join(' ');
  }

  constructor(props) {
    super(props);

    this.state = {
      isEditing: false,
    };
  }

  setEditMode = (isEditing: boolean) => {
    this.setState({ isEditing });
  };

  toggleEdit = (e: React.MouseEvent<HTMLButtonElement>) => {
    const { isEditing } = this.state;
    const { title } = this.props;
    const logTitle = EditableSection.convertText(title);

    this.setState({ isEditing: !isEditing });
    logClick(e, {
      label: 'Toggle Editable Section',
      target_id: `toggle-edit-${logTitle.toLowerCase()}-section`,
    });
  };

  preventDefault = (event: React.MouseEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  renderButton = (): React.ReactNode => {
    const { isEditing } = this.state;

    return (
      <button
        type="button"
        className={`btn btn-flat-icon edit-button ${isEditing ? 'active' : ''}`}
        onClick={this.toggleEdit}
      >
        <span className="sr-only">{Constants.EDIT_TEXT}</span>
        <img
          className={`icon icon-small icon-edit ${
            isEditing ? 'icon-color' : ''
          }`}
          alt=""
        />
      </button>
    );
  };

  renderReadOnlyButton = (): React.ReactNode => {
    const { editText, editUrl } = this.props;
    const popoverHoverFocus = (
      <Popover id="popover-trigger-hover-focus">{editText}</Popover>
    );

    if (!editUrl) {
      return null;
    }

    return (
      <OverlayTrigger
        trigger={['hover', 'focus']}
        placement="top"
        overlay={popoverHoverFocus}
      >
        <a
          className="btn btn-flat-icon-dark edit-button"
          href={editUrl}
          target="_blank"
          rel="noopener noreferrer"
        >
          <span className="sr-only">{Constants.EDIT_TEXT}</span>
          <img className="icon icon-small icon-edit" alt="" />
        </a>
      </OverlayTrigger>
    );
  };

  render() {
    const { children, title, readOnly = false } = this.props;
    const { isEditing } = this.state;

    const childrenWithProps = React.Children.map(children, (child) => {
      if (!React.isValidElement(child)) {
        return child;
      }

      return React.cloneElement(child, {
        readOnly,
        isEditing,
        setEditMode: this.setEditMode,
      });
    });

    return (
      <section className="editable-section">
        <label className="editable-section-label">
          <div
            className="editable-section-label-wrapper"
            onClick={!readOnly ? this.preventDefault : undefined}
          >
            <span className="section-title title-3">
              {EditableSection.convertText(title)}
            </span>
            {!readOnly ? this.renderButton() : this.renderReadOnlyButton()}
          </div>
        </label>
        <div className="editable-section-content">{childrenWithProps}</div>
      </section>
    );
  }
}

export default EditableSection;
