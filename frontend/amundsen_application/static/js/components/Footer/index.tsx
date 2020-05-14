import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
// TODO: Use css-modules instead of 'import'
import './styles.scss';
import { GlobalState } from 'ducks/rootReducer';
import { getLastIndexed } from 'ducks/tableMetadata/reducer';
import { GetLastIndexedRequest } from 'ducks/tableMetadata/types';

import { formatDateTimeLong } from 'utils/dateUtils';

// Props
interface StateFromProps {
  lastIndexed: number;
}

interface DispatchFromProps {
  getLastIndexed: () => GetLastIndexedRequest;
}

export type FooterProps = StateFromProps & DispatchFromProps;

export class Footer extends React.Component<FooterProps> {
  componentDidMount() {
    this.props.getLastIndexed();
  }

  generateDateTimeString = () => {
    return formatDateTimeLong({ epochTimestamp: this.props.lastIndexed });
  };

  render() {
    let content;
    if (!!this.props.lastIndexed) {
      content = <div>{`Amundsen was last indexed on ${this.generateDateTimeString()}`}</div>;
    }
    return (
      <div>
        <div className="phantom-div" />
        <div id="footer" className="footer">
          { content }
        </div>
      </div>
    );
  }
}


export const mapStateToProps = (state: GlobalState) => {
  return {
    lastIndexed: state.tableMetadata.lastIndexed
  }
};

export const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({ getLastIndexed }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps>(mapStateToProps, mapDispatchToProps)(Footer);
