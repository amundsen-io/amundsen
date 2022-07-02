// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Modal, OverlayTrigger, Popover } from 'react-bootstrap';

import './styles.scss';

import { logClick } from 'utils/analytics';
import {
  getTruncatedText,
  parseNestedType,
  NestedType,
  ParsedType,
} from './parser';
import {
  CTA_TEXT,
  MODAL_TITLE,
  TEXT_INDENT,
  MAX_DISPLAY_TYPE_LENGTH,
} from './constants';

export interface ColumnTypeProps {
  columnName: string;
  database: string;
  type: string;
}

export interface ColumnTypeState {
  showModal: boolean;
}

export class ColumnType extends React.Component<
  ColumnTypeProps,
  ColumnTypeState
> {
  constructor(props) {
    super(props);

    this.state = {
      showModal: false,
    };
  }

  nestedType: NestedType | null;

  hideModal = (e) => {
    this.stopPropagation(e);
    this.setState({ showModal: false });
  };

  showModal = (e) => {
    logClick(e);
    this.stopPropagation(e);
    this.setState({ showModal: true });
  };

  stopPropagation = (e) => {
    if (e) {
      e.stopPropagation();
    }
  };

  createLineItem = (text: string, textIndent: number) => (
    <div key={`lineitem:${text}`} style={{ textIndent: `${textIndent}px` }}>
      {text}
    </div>
  );

  renderParsedChildren = (children: ParsedType[], level: number) => {
    const textIndent = level * TEXT_INDENT;
    return children.map((item) => {
      if (typeof item === 'string') {
        return this.createLineItem(item, textIndent);
      }
      return this.renderNestedType(item, level);
    });
  };

  renderNestedType = (nestedType: NestedType, level: number = 0) => {
    const { head, tail, children } = nestedType;
    const textIndent = level * TEXT_INDENT;
    return (
      <div key={`nesteditem:${head}${tail}`}>
        {this.createLineItem(head, textIndent)}
        {this.renderParsedChildren(children, level + 1)}
        {this.createLineItem(tail, textIndent)}
      </div>
    );
  };

  render = () => {
    const { showModal } = this.state;
    const { columnName, database, type } = this.props;
    this.nestedType = parseNestedType(type, database);
    if (this.nestedType === null) {
      return <p className="column-type">{type}</p>;
    }

    const hasLongTypeString =
      this.nestedType.col_type &&
      this.nestedType.col_type.length > MAX_DISPLAY_TYPE_LENGTH;
    const popoverHover = (
      <Popover
        className="column-type-popover"
        id={`column-type-popover:${columnName}`}
      >
        {CTA_TEXT}
      </Popover>
    );
    return (
      <div onClick={this.stopPropagation}>
        <OverlayTrigger
          trigger={['hover', 'focus']}
          placement="top"
          overlay={popoverHover}
          rootClose
        >
          <button
            data-type="column-type"
            type="button"
            className="column-type-btn"
            onClick={this.showModal}
          >
            {this.nestedType.col_type && !hasLongTypeString
              ? this.nestedType.col_type
              : getTruncatedText(this.nestedType)}
          </button>
        </OverlayTrigger>
        <Modal
          className="column-type-modal"
          show={showModal}
          onHide={this.hideModal}
        >
          <Modal.Header closeButton>
            <Modal.Title>
              <div className="main-title">{MODAL_TITLE}</div>
              <div className="sub-title">{columnName}</div>
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="column-type-modal-content">
              {this.renderNestedType(this.nestedType)}
            </div>
          </Modal.Body>
        </Modal>
      </div>
    );
  };
}

export default ColumnType;
