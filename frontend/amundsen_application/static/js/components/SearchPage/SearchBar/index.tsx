import * as React from 'react';
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import {
  ERROR_CLASSNAME,
  PLACEHOLDER_DEFAULT,
  SUBTEXT_DEFAULT,
  SYNTAX_ERROR_CATEGORY,
  SYNTAX_ERROR_PREFIX,
  SYNTAX_ERROR_SPACING_SUFFIX,
} from './constants';
import { GlobalState } from 'ducks/rootReducer';
import { submitSearch } from 'ducks/search/reducer';
import { SubmitSearchRequest } from 'ducks/search/types';

export interface StateFromProps {
  searchTerm: string;
}

export interface DispatchFromProps {
  submitSearch: (searchTerm: string) => SubmitSearchRequest;
}

export interface OwnProps {
  placeholder?: string;
  subText?: string;
}

export type SearchBarProps = StateFromProps & DispatchFromProps & OwnProps;

interface SearchBarState {
  subTextClassName: string;
  searchTerm: string;
  subText: string;
}

export class SearchBar extends React.Component<SearchBarProps, SearchBarState> {
  public static defaultProps: Partial<SearchBarProps> = {
    placeholder: PLACEHOLDER_DEFAULT,
    subText: SUBTEXT_DEFAULT,
  };

  constructor(props) {
    super(props);

    this.state = {
      subTextClassName: '',
      searchTerm: this.props.searchTerm,
      subText: this.props.subText,
    };
  }

  static getDerivedStateFromProps(props, state) {
    const { searchTerm } = props;
    return { searchTerm };
  }

  handleValueChange = (event: React.SyntheticEvent<HTMLInputElement>) : void => {
    this.setState({ searchTerm: (event.target as HTMLInputElement).value.toLowerCase() });
  };

  handleValueSubmit = (event: React.FormEvent<HTMLFormElement>) : void => {
    const searchTerm = this.state.searchTerm.trim();
    event.preventDefault();
    if (this.isFormValid(searchTerm)) {
      this.props.submitSearch(searchTerm);
    }
  };

  isFormValid = (searchTerm: string) : boolean => {
    if (searchTerm.length === 0) {
      return false;
    }

    const hasAtMostOneCategory = searchTerm.split(':').length <= 2;
    if (!hasAtMostOneCategory) {
      this.setState({
        subText: SYNTAX_ERROR_CATEGORY,
        subTextClassName: ERROR_CLASSNAME,
      });
      return false;
    }

    const colonIndex = searchTerm.indexOf(':');
    const hasNoSpaceAroundColon = colonIndex < 0 ||
      (colonIndex >= 1 && searchTerm.charAt(colonIndex+1) !== " " &&  searchTerm.charAt(colonIndex-1) !== " ");
    if (!hasNoSpaceAroundColon) {
      this.setState({
        subText: `${SYNTAX_ERROR_PREFIX}'${searchTerm.substring(0,colonIndex).trim()}:${searchTerm.substring(colonIndex+1).trim()}'${SYNTAX_ERROR_SPACING_SUFFIX}`,
        subTextClassName: ERROR_CLASSNAME,
      });
      return false;
    }

    this.setState({ subText: SUBTEXT_DEFAULT, subTextClassName: "" });
    return true;
  };

  render() {
    const subTextClass = `subtext body-secondary-3 ${this.state.subTextClassName}`;
    return (
      <div id="search-bar">
        <form className="search-bar-form" onSubmit={ this.handleValueSubmit }>
            <input
              id="search-input"
              className="h2 search-bar-input form-control"
              value={ this.state.searchTerm }
              onChange={ this.handleValueChange }
              aria-label={ this.props.placeholder }
              placeholder={ this.props.placeholder }
              autoFocus={ true }
            />
          <button className="btn btn-flat-icon search-bar-button" type="submit">
            <img className="icon icon-search" />
          </button>
        </form>
        <div className={ subTextClass }>
          { this.state.subText }
        </div>
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  return {
    searchTerm: state.search.search_term,
  };
};

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ submitSearch }, dispatch);
};

export default connect<StateFromProps>(mapStateToProps, mapDispatchToProps)(SearchBar);
