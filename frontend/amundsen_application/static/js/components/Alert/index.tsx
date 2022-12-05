// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import SanitizedHTML from 'react-sanitized-html';

import { IconSizes } from 'interfaces';
import { NoticeSeverity } from 'config/config-types';
import { AlertIcon, InformationIcon } from 'components/SVGIcons';

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
}

const Alert: React.FC<AlertProps> = ({
  message,
  severity = NoticeSeverity.WARNING,
  onAction,
  actionText,
  actionHref,
  actionLink,
}: AlertProps) => {
  let action: null | React.ReactNode = null;

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

  return (
    <div className={`alert ${SEVERITY_TO_SEVERITY_CLASS[severity]}`}>
      {iconComponent}
      <p className="alert-message">{formattedMessage}</p>
      {action && <span className="alert-action">{action}</span>}
    </div>
  );
};

export default Alert;
