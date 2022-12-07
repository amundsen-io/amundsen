// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import SanitizedHTML from 'react-sanitized-html';
import { Modal } from 'react-bootstrap';

import { IconSizes } from 'interfaces';
import { NoticeSeverity } from 'config/config-types';
import { AlertIcon, InformationIcon } from 'components/SVGIcons';
import { DefinitionList } from 'components/DefinitionList';

import './styles.scss';

const SEVERITY_TO_COLOR_MAP = {
  [NoticeSeverity.INFO]: '#3a97d3', // cyan50
  [NoticeSeverity.WARNING]: '#ffb146', // $amber50
  [NoticeSeverity.ALERT]: '#b8072c', // $red70
};
const SEVERITY_TO_SEVERITY_CLASS = {
  [NoticeSeverity.INFO]: 'is-info',
  [NoticeSeverity.WARNING]: 'is-warning',
  [NoticeSeverity.ALERT]: 'is-alert',
};
const OPEN_PAYLOAD_CTA = 'See details';
const PAYLOAD_MODAL_TITLE = 'Summary';
const PAYLOAD_MODAL_CLOSE_BTN = 'Close';

export interface AlertProps {
  /** Message to show in the alert */
  message: string | React.ReactNode;
  /** Severity of the alert (info, warning, or alert) */
  severity?: NoticeSeverity;
  /** Link passed to set as the action (for routing links) */
  actionLink?: React.ReactNode;
  /** Text of the link action */
  actionText?: string;
  /** Href for the link action */
  actionHref?: string;
  /** Callback to call when the action is clicked */
  onAction?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Optional extra info to render in a modal */
  payload?: Record<string, string>;
}

const Alert: React.FC<AlertProps> = ({
  message,
  severity = NoticeSeverity.WARNING,
  onAction,
  actionText,
  actionHref,
  actionLink,
  payload,
}: AlertProps) => {
  const [showPayloadModal, setShowPayloadModal] = React.useState(false);
  let action: null | React.ReactNode = null;

  const handleSeeDetails = (e: React.MouseEvent<HTMLButtonElement>) => {
    onAction?.(e);
    setShowPayloadModal(true);
  };
  const handleModalClose = () => {
    setShowPayloadModal(false);
  };

  if (payload) {
    action = (
      <button
        type="button"
        className="btn btn-link btn-payload"
        onClick={handleSeeDetails}
      >
        {OPEN_PAYLOAD_CTA}
      </button>
    );
  }

  if (actionText && onAction) {
    action = (
      <button type="button" className="btn btn-link" onClick={onAction}>
        {actionText}
      </button>
    );
  }

  if (actionText && actionHref) {
    action = (
      <a className="action-link" href={actionHref}>
        {actionText}
      </a>
    );
  }

  if (actionLink) {
    action = actionLink;
  }

  let iconComponent: React.ReactNode = null;

  if (severity === NoticeSeverity.INFO) {
    iconComponent = (
      <InformationIcon
        fill={SEVERITY_TO_COLOR_MAP[severity]}
        size={IconSizes.REGULAR}
      />
    );
  } else {
    iconComponent = (
      <AlertIcon
        stroke={SEVERITY_TO_COLOR_MAP[severity]}
        size={IconSizes.SMALL}
      />
    );
  }

  // If we receive a string, we want to sanitize any html inside
  const formattedMessage =
    typeof message === 'string' ? <SanitizedHTML html={message} /> : message;

  const payloadDefinitions = payload
    ? Object.keys(payload).map((key) => ({
        term: key,
        description: payload[key],
      }))
    : null;

  return (
    <div className={`alert ${SEVERITY_TO_SEVERITY_CLASS[severity]}`}>
      {iconComponent}
      <p className="alert-message">{formattedMessage}</p>
      {action && <span className="alert-action">{action}</span>}
      {payloadDefinitions && (
        <Modal
          className="alert-payload-modal"
          show={showPayloadModal}
          onHide={handleModalClose}
        >
          <Modal.Header closeButton onHide={handleModalClose}>
            <Modal.Title>{PAYLOAD_MODAL_TITLE}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <DefinitionList definitions={payloadDefinitions} termWidth={120} />
          </Modal.Body>
          <Modal.Footer>
            <button
              className="btn btn-primary payload-modal-close"
              type="button"
              onClick={handleModalClose}
            >
              {PAYLOAD_MODAL_CLOSE_BTN}
            </button>
          </Modal.Footer>
        </Modal>
      )}
    </div>
  );
};

export default Alert;
