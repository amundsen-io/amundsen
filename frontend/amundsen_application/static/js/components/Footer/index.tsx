import * as React from 'react';
import moment from 'moment-timezone';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
// TODO: Use css-modules instead of 'import'
import './styles.scss';
import { GlobalState } from "../../ducks/rootReducer";
import { getLastIndexed } from "../../ducks/tableMetadata/reducer";
import { GetLastIndexedRequest } from "../../ducks/tableMetadata/types";

// Props
interface StateFromProps {
  lastIndexed: number;
}

interface DispatchFromProps {
  getLastIndexed: () => GetLastIndexedRequest;
}

type FooterProps = StateFromProps & DispatchFromProps;

// State
interface FooterState {
  lastIndexed: number;
}

export class Footer extends React.Component<FooterProps, FooterState> {
  constructor(props) {
    super(props);

    this.state = {
      lastIndexed: this.props.lastIndexed,
    };
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    const { lastIndexed } = nextProps;
    return { lastIndexed };
  }

  componentDidMount() {
    this.props.getLastIndexed();
  }

  render() {
    let content;
    if (this.state.lastIndexed !== null) {
      // 'moment.local' will utilize the client's local timezone.
      const dateTimeString = moment.unix(this.state.lastIndexed).local().format('MMMM Do YYYY [at] h:mm:ss a');
      content = <div>{`Amundsen was last indexed on ${dateTimeString}`}</div>;
    }
    return (
      <div>
        <div className="phantom-div" />
        <div className="footer">
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
