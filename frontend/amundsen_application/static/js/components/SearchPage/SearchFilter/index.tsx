import * as React from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import { GlobalState } from 'ducks/rootReducer';

import CheckBoxItem from 'components/common/Inputs/CheckBoxItem';

import './styles.scss'

interface SearchFilterInput {
  value: string;
  labelText: string;
  checked: boolean;
  count: number;
}

interface SearchFilterSection {
  title: string;
  categoryId: string;
  inputProperties: SearchFilterInput[];
}

/*
  TODO: Change on what becomes necessary for implementation
*/
export interface StateFromProps {
  checkBoxSections: SearchFilterSection[];
}

/*
  TODO: Delete if not necessary for final implementation
*/
export interface OwnProps {
}

/*
  TODO: onFilterChange dispatched action to update filters. Consider:
  1. Payload could contain categoryId and valueId and what to do with it
     e.g. - {categoryId: 'datasets', value: 'hive', checked: false }
  2. Disable component until implementing for user friendly debouncing
  3. On success - Re-enable, checkedUI should update based on new state
  4. On failure - Re-enable, state will not have been updated on failure,
                  checkedUI stays the same.
*/
export interface DispatchFromProps {
  onFilterChange: () => any;
}

export type SearchFilterProps = StateFromProps & OwnProps & DispatchFromProps;

export class SearchFilter extends React.Component<SearchFilterProps> {
  constructor(props) {
    super(props);
  }

  createCheckBoxItem = (item: SearchFilterInput, categoryId: string, key: string) => {
    const dummyMethod = () => { console.log('Dispatched') };
    const { checked, count, labelText, value } = item;
    return (
      <CheckBoxItem
        key={key}
        checked={ checked }
        disabled={ count === 0 }
        name={ categoryId }
        value={ value }
        onChange={ dummyMethod }>
          <span className="subtitle-2">{ labelText }</span>
          <span className="body-secondary-3 pull-right">{ count }</span>
      </CheckBoxItem>
    );
  };

  createCheckBoxSection = (section: SearchFilterSection, key: string) => {
    const { categoryId, inputProperties, title } = section;
    return (
      <div key={key} className="search-filter-section">
        <div className="title-2">{ title }</div>
        { inputProperties.map((item, index) => this.createCheckBoxItem(item, categoryId, `item:${categoryId}:${index}`)) }
      </div>
    );
  };

  render = () => {
    return this.props.checkBoxSections.map((section, index) => this.createCheckBoxSection(section, `section:${index}`));
  };
};

/*
  TODO: Process the global state however needed to get the necessary props
  The dummy checkBoxSections property shape below is not expected to mirror how we store
  filters and results in the globalState. Rather let checkBoxSections be the data shape
  that works best for the component and mapStateToProps wiill translate globalState -> checkBoxSections.
*/
export const mapStateToProps = (state: GlobalState) => {
  return {
    checkBoxSections: [
      {
        title: 'Type', // category.displayName
        categoryId: 'datasets', // category.id
        inputProperties: [
          {
            value: 'bigquery', // value.id
            labelText: 'BigQuery', // value.displayName
            checked: true, // pull value or infer value from state
            count: 100, // pull value from state
          },
          {
            value: 'hive', // value.id
            labelText: 'Hive', // value.displayName
            checked: true, // pull value or infer value from state
            count: 100, // pull value from state
          },
          {
            value: 'druid', // value.id
            labelText: 'Druid', // value.displayName
            checked: true, // pull value or infer value from state
            count: 0, // pull value from state
          },
          {
            value: 's3', // value.id
            labelText: 'S3 Buckets', // value.displayName
            checked: false, // pull value or infer value from state
            count: 100, // pull value from state
          }
        ]
      },
      {
        title: 'Badges', // category.displayName
        categoryId: 'badges', // category.id
        inputProperties: [
          {
            value: 'sla', // value.id
            labelText: 'Missed SLA', // value.displayName
            checked: true, // pull value or infer value from state
            count: 3, // pull value from state
          },
          {
            value: 'quality', // value.id
            labelText: 'High Quality', // value.displayName
            checked: true, // pull value or infer value from state
            count: 12, // pull value from state
          },
          {
            value: 'pii', // value.id
            labelText: 'PII', // value.displayName
            checked: false, // pull value or infer value from state
            count: 34, // pull value from state
          },
          {
            value: 'deprecated', // value.id
            labelText: 'Deprecated', // value.displayName
            checked: false, // pull value or infer value from state
            count: 3, // pull value from state
          }
        ]
      }
    ]
  };
};

/*
  TODO: Dispatch a real action
*/
export const mapDispatchToProps = (dispatch: any) => {
  // return bindActionCreators({ onFilterChange } , dispatch);
};

export default connect<StateFromProps, DispatchFromProps, OwnProps>(mapStateToProps)(SearchFilter);
