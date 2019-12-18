import * as React from 'react';
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux';

import { GlobalState } from 'ducks/rootReducer';
import { submitSearch, getInlineResultsDebounce, selectInlineResult } from 'ducks/search/reducer';
import { SubmitSearchRequest, InlineSearchRequest, InlineSearchSelect } from 'ducks/search/types';

import { ResourceType } from 'interfaces';

import InlineSearchResults from './InlineSearchResults';

import './styles.scss';

import {
  BUTTON_CLOSE_TEXT,
  ERROR_CLASSNAME,
  PLACEHOLDER_DEFAULT,
  SIZE_SMALL,
  SUBTEXT_DEFAULT,
  SYNTAX_ERROR_CATEGORY,
  SYNTAX_ERROR_PREFIX,
  SYNTAX_ERROR_SPACING_SUFFIX,
} from './constants';

export interface StateFromProps {
  searchTerm: string;
}

export interface DispatchFromProps {
  submitSearch: (searchTerm: string) => SubmitSearchRequest;
  onInputChange: (term: string) => InlineSearchRequest;
  onSelectInlineResult: (resourceType: ResourceType, searchTerm: string, updateUrl: boolean) => InlineSearchSelect;
}

export interface OwnProps {
  placeholder?: string;
  subText?: string;
  size?: string;
}

export type SearchBarProps = StateFromProps & DispatchFromProps & OwnProps;

interface SearchBarState {
  showTypeAhead: boolean;
  subTextClassName: string;
  searchTerm: string;
  subText: string;
}

export class SearchBar extends React.Component<SearchBarProps, SearchBarState> {
  private refToSelf: React.RefObject<HTMLDivElement>;

  public static defaultProps: Partial<SearchBarProps> = {
    placeholder: PLACEHOLDER_DEFAULT,
    subText: SUBTEXT_DEFAULT,
    size: '',
  };

  constructor(props) {
    super(props);
    this.refToSelf = React.createRef<HTMLDivElement>();

    this.state = {
      showTypeAhead: false,
      subTextClassName: '',
      searchTerm: this.props.searchTerm,
      subText: this.props.subText,
    };
  }

  clearSearchTerm = () : void => {
    this.setState({ showTypeAhead: false, searchTerm: '' });
  };

  componentDidMount = () => {
    document.addEventListener('mousedown', this.updateTypeAhead, false);
  };

  componentWillUnmount = () => {
    document.removeEventListener('mousedown', this.updateTypeAhead, false);
  };

  componentDidUpdate = (prevProps: SearchBarProps) => {
    if (this.props.searchTerm !== prevProps.searchTerm) {
      this.setState({ searchTerm: this.props.searchTerm });
    }
  };

  handleValueChange = (event: React.SyntheticEvent<HTMLInputElement>) : void => {
    const searchTerm = (event.target as HTMLInputElement).value.toLowerCase();
    const showTypeAhead = this.shouldShowTypeAhead(searchTerm);
    this.setState({ searchTerm, showTypeAhead });

    if (showTypeAhead) {
      this.props.onInputChange(searchTerm);
    }
  };

  handleValueSubmit = (event: React.FormEvent<HTMLFormElement>) : void => {
    const searchTerm = this.state.searchTerm.trim();
    event.preventDefault();
    if (this.isFormValid(searchTerm)) {
      this.props.submitSearch(searchTerm);
      this.hideTypeAhead();
    }
  };

  hideTypeAhead = () : void => {
    this.setState({ showTypeAhead: false });
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

  onSelectInlineResult = (resourceType: ResourceType, updateUrl: boolean = false) : void => {
    this.hideTypeAhead();
    this.props.onSelectInlineResult(resourceType, this.state.searchTerm, updateUrl);
  }

  shouldShowTypeAhead = (searchTerm: string) : boolean => {
    return searchTerm.length > 0;
  }

  updateTypeAhead = (event: Event): void => {
    /* This logic will hide/show the inline results component when the user clicks
      outside/inside of the search bar */
    if (this.refToSelf.current && this.refToSelf.current.contains(event.target as Node)) {
      this.setState({ showTypeAhead: this.shouldShowTypeAhead(this.state.searchTerm) });
    } else {
      this.hideTypeAhead();
    }
  };

  render() {
    const inputClass = `${this.props.size === SIZE_SMALL ? 'title-2 small' : 'h2 large'} search-bar-input form-control`;
    const searchButtonClass = `btn btn-flat-icon search-button ${this.props.size === SIZE_SMALL ? 'small' : 'large'}`;
    const subTextClass = `subtext body-secondary-3 ${this.state.subTextClassName}`;

    return (
      <div id="search-bar" ref={this.refToSelf}>
        <form className="search-bar-form" onSubmit={ this.handleValueSubmit }>
            <input
              id="search-input"
              className={ inputClass }
              value={ this.state.searchTerm }
              onChange={ this.handleValueChange }
              aria-label={ this.props.placeholder }
              placeholder={ this.props.placeholder }
              autoFocus={ true }
              autoComplete="off"
            />
          <button className={ searchButtonClass } type="submit">
            <img className="icon icon-search" />
          </button>
          {
            this.props.size === SIZE_SMALL &&
            <button type="button" className="btn btn-close clear-button" aria-label={BUTTON_CLOSE_TEXT} onClick={this.clearSearchTerm} />
          }
        </form>
        {
          this.state.showTypeAhead &&
          // @ts-ignore: Investigate proper configuration for 'className' to be valid by default on custom components
          <InlineSearchResults
            className={this.props.size === SIZE_SMALL ? 'small' : ''}
            onItemSelect={this.onSelectInlineResult}
            searchTerm={this.state.searchTerm}
          />
        }
        {
          this.props.size !== SIZE_SMALL &&
          <div className={ subTextClass }>
            { this.state.subText }
          </div>
        }
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
  return bindActionCreators({ submitSearch, onInputChange: getInlineResultsDebounce, onSelectInlineResult: selectInlineResult }, dispatch);
};

export default connect<StateFromProps, DispatchFromProps, OwnProps>(mapStateToProps,  mapDispatchToProps)(SearchBar);
