// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { connect } from 'react-redux';
import { OpenRequestAction } from 'ducks/notification/types';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { bindActionCreators } from 'redux';
import { RequestMetadataType } from 'interfaces';
import { REQUEST_DESCRIPTION } from './constants';
import './styles.scss';

export interface RequestDescriptionTextOwnProps {
  requestMetadataType: RequestMetadataType;
  columnName?: string;
}

export interface DispatchFromProps {
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName?: string
  ) => OpenRequestAction;
}

export type RequestDescriptionTextProps = RequestDescriptionTextOwnProps &
  DispatchFromProps;

export const RequestDescriptionText: React.FC<RequestDescriptionTextProps> = ({
  requestMetadataType,
  columnName,
  openRequestDescriptionDialog,
}) => {
  const openRequest = () => {
    openRequestDescriptionDialog(requestMetadataType, columnName);
  };

  return (
    <button
      className="request-description body-link"
      type="button"
      onClick={openRequest}
    >
      {REQUEST_DESCRIPTION}
    </button>
  );
};

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ openRequestDescriptionDialog }, dispatch);

export default connect<{}, DispatchFromProps>(
  null,
  mapDispatchToProps
)(RequestDescriptionText);
