import * as React from 'react';
import './styles.scss';

import { GlobalState } from 'ducks/rootReducer';
import { connect } from 'react-redux';
import { OpenRequestAction } from 'ducks/notification/types';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { bindActionCreators } from 'redux';
import { REQUEST_DESCRIPTION } from './constants';

import { RequestMetadataType } from 'interfaces';

export interface DispatchFromProps {
  openRequestDescriptionDialog: (requestMetadataType: RequestMetadataType) => OpenRequestAction;
}

export type RequestDescriptionTextProps = DispatchFromProps;

interface RequestDescriptionTextState {}

export class RequestDescriptionText extends React.Component<RequestDescriptionTextProps, RequestDescriptionTextState> {
  public static defaultProps: Partial<RequestDescriptionTextProps> = {};

  constructor(props) {
    super(props);
  }

  openRequest = () => {
    this.props.openRequestDescriptionDialog(RequestMetadataType.TABLE_DESCRIPTION);
  }

  render() {
    return (
      <a className="request-description"
        href="JavaScript:void(0)"
        onClick={ this.openRequest }
      >
       { REQUEST_DESCRIPTION }
      </a>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ openRequestDescriptionDialog } , dispatch);
};

export default connect<{}, DispatchFromProps>(null, mapDispatchToProps)(RequestDescriptionText);
