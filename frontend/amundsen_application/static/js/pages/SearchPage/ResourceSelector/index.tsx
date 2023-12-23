// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import {
  indexDashboardsEnabled,
  indexFeaturesEnabled,
  indexUsersEnabled,
  indexFilesEnabled,
  indexProvidersEnabled,
} from 'config/config-utils';
import { GlobalState } from 'ducks/rootReducer';
import { updateSearchState } from 'ducks/search/reducer';
import {
  DashboardSearchResults,
  FeatureSearchResults,
  TableSearchResults,
  UpdateSearchStateRequest,
  UserSearchResults,
  FileSearchResults,
  ProviderSearchResults,
} from 'ducks/search/types';
import { ResourceType } from 'interfaces/Resources';
import { logClick } from 'utils/analytics';
import {
  DASHBOARD_RESOURCE_TITLE,
  FEATURE_RESOURCE_TITLE,
  TABLE_RESOURCE_TITLE,
  USER_RESOURCE_TITLE,
  FILE_RESOURCE_TITLE,
  PROVIDER_RESOURCE_TITLE,
} from '../constants';

const RESOURCE_SELECTOR_TITLE = 'Resource';

export interface StateFromProps {
  resource: ResourceType;
  tables: TableSearchResults;
  dashboards: DashboardSearchResults;
  users: UserSearchResults;
  features: FeatureSearchResults;
  files: FileSearchResults;
  providers: ProviderSearchResults;
}

export interface DispatchFromProps {
  setResource: (resource: ResourceType) => UpdateSearchStateRequest;
}

export type ResourceSelectorProps = StateFromProps & DispatchFromProps;

interface ResourceOptionConfig {
  type: ResourceType;
  label: string;
  count: number;
}

export class ResourceSelector extends React.Component<ResourceSelectorProps> {
  onChange = (event) => {
    const { setResource } = this.props;

    setResource(event.target.value);
  };

  renderRadioOption = (option: ResourceOptionConfig, index: number) => (
    <div key={`resource-radio-item:${index}`} className="radio">
      <label className="radio-label">
        <input
          type="radio"
          name="resource"
          value={option.type}
          aria-label={option.type}
          checked={this.props.resource === option.type}
          onClick={(e) =>
            logClick(e, {
              target_id: 'search_resource_selector',
              value: option.type,
            })
          }
          onChange={this.onChange}
        />
        <span className="text-subtitle-w2">{option.label}</span>
        <span className="body-secondary-3 pull-right">{option.count}</span>
      </label>
    </div>
  );

  render = () => {
    const { tables, dashboards, users, features, files, providers } = this.props;

    const resourceOptions = [
      {
        type: ResourceType.table,
        label: TABLE_RESOURCE_TITLE,
        count: tables.total_results,
      },
    ];

    if (indexDashboardsEnabled()) {
      resourceOptions.push({
        type: ResourceType.dashboard,
        label: DASHBOARD_RESOURCE_TITLE,
        count: dashboards.total_results,
      });
    }

    if (indexUsersEnabled()) {
      resourceOptions.push({
        type: ResourceType.user,
        label: USER_RESOURCE_TITLE,
        count: users.total_results,
      });
    }

    if (indexFeaturesEnabled()) {
      resourceOptions.push({
        type: ResourceType.feature,
        label: FEATURE_RESOURCE_TITLE,
        count: features.total_results,
      });
    }

    console.log(indexFilesEnabled());
    
    if (indexFilesEnabled()) {
      resourceOptions.push({
        type: ResourceType.file,
        label: FILE_RESOURCE_TITLE,
        count: files.total_results,
      });
    }

    if (indexProvidersEnabled()) {
      resourceOptions.push({
        type: ResourceType.provider,
        label: PROVIDER_RESOURCE_TITLE,
        count: providers.total_results,
      });
    }

    return (
      <>
        <h2 className="title-2">{RESOURCE_SELECTOR_TITLE}</h2>
        {resourceOptions.map((option, index) =>
          this.renderRadioOption(option, index)
        )}
      </>
    );
  };
}

export const mapStateToProps = (state: GlobalState) => ({
  resource: state.search.resource,
  tables: state.search.tables,
  users: state.search.users,
  dashboards: state.search.dashboards,
  features: state.search.features,
  files: state.search.files,
  providers: state.search.providers,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      setResource: (resource: ResourceType) =>
        updateSearchState({ resource, updateUrl: true }),
    },
    dispatch
  );

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(ResourceSelector);
