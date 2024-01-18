// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { connect } from 'react-redux';

import {
  getSourceDisplayName,
  getSourceIconClass,
  indexDashboardsEnabled,
  indexFeaturesEnabled,
  indexUsersEnabled,
  indexFilesEnabled,
  indexProvidersEnabled,
} from 'config/config-utils';
import { buildDashboardURL } from 'utils/navigation';

import { GlobalState } from 'ducks/rootReducer';
import {
  DashboardSearchResults,
  FeatureSearchResults,
  TableSearchResults,
  UserSearchResults,
  FileSearchResults,
  DataProviderSearchResults,
} from 'ducks/search/types';

import {
  Resource,
  ResourceType,
  DashboardResource,
  FeatureResource,
  TableResource,
  UserResource,
  FileResource,
  DataProviderResource,
} from 'interfaces';

import ResultItemList, { SuggestedResult } from './ResultItemList';
import SearchItemList from './SearchItemList';

import './styles.scss';

import * as CONSTANTS from './constants';

export interface StateFromProps {
  isLoading: boolean;
  dashboards: DashboardSearchResults;
  features: FeatureSearchResults;
  tables: TableSearchResults;
  users: UserSearchResults;
  files: FileSearchResults;
  providers: DataProviderSearchResults;
}

export interface OwnProps {
  className?: string;
  onItemSelect: (resourceType: ResourceType, updateUrl?: boolean) => void;
  searchTerm: string;
}

export type InlineSearchResultsProps = StateFromProps & OwnProps;

export class InlineSearchResults extends React.Component<
  InlineSearchResultsProps,
  {}
> {
  getTitleForResource = (resourceType: ResourceType): string => {
    switch (resourceType) {
      case ResourceType.dashboard:
        return CONSTANTS.DASHBOARDS;
      case ResourceType.feature:
        return CONSTANTS.FEATURES;
      case ResourceType.table:
        return CONSTANTS.DATASETS;
      case ResourceType.user:
        return CONSTANTS.PEOPLE;
      case ResourceType.file:
        return CONSTANTS.FILES;
      case ResourceType.data_provider:
        return CONSTANTS.PROVIDERS;
      default:
        return '';
    }
  };

  getTotalResultsForResource = (resourceType: ResourceType): number => {
    const { dashboards, features, tables, users, files, providers } = this.props;

    switch (resourceType) {
      case ResourceType.dashboard:
        return dashboards.total_results;
      case ResourceType.feature:
        return features.total_results;
      case ResourceType.table:
        return tables.total_results;
      case ResourceType.user:
        return users.total_results;
      case ResourceType.file:
        return files.total_results;
      case ResourceType.data_provider:
        return providers.total_results;
      default:
        return 0;
    }
  };

  getResultsForResource = (resourceType: ResourceType): Resource[] => {
    const { dashboards, features, tables, users, files, providers } = this.props;

    switch (resourceType) {
      case ResourceType.dashboard:
        return dashboards.results.slice(0, 2);
      case ResourceType.feature:
        return features.results.slice(0, 2);
      case ResourceType.table:
        return tables.results.slice(0, 2);
      case ResourceType.user:
        return users.results.slice(0, 2);
      case ResourceType.file:
        return files.results.slice(0, 2);
      case ResourceType.data_provider:
        return providers.results.slice(0, 2);
      default:
        return [];
    }
  };

  getSuggestedResultsForResource = (
    resourceType: ResourceType
  ): SuggestedResult[] => {
    const results = this.getResultsForResource(resourceType);

    return results.map((result, index) => ({
      href: this.getSuggestedResultHref(resourceType, result, index),
      iconClass: this.getSuggestedResultIconClass(resourceType, result),
      subtitle: this.getSuggestedResultSubTitle(resourceType, result),
      titleNode: this.getSuggestedResultTitle(resourceType, result),
      type: this.getSuggestedResultType(resourceType, result),
    }));
  };

  getSuggestedResultHref = (
    resourceType: ResourceType,
    result: Resource,
    index: number
  ): string => {
    const logParams = `source=inline_search&index=${index}`;

    switch (resourceType) {
      case ResourceType.dashboard: {
        const dashboard = result as DashboardResource;

        return `${buildDashboardURL(dashboard.uri)}?${logParams}`;
      }
      case ResourceType.feature: {
        const feature = result as FeatureResource;

        return `/feature/${feature.feature_group}/${feature.name}/${feature.version}?${logParams}`;
      }
      case ResourceType.table: {
        const table = result as TableResource;

        return `/table_detail/${table.cluster}/${table.database}/${table.schema}/${table.name}?${logParams}`;
      }
      case ResourceType.user: {
        const user = result as UserResource;

        return `/user/${user.user_id}?${logParams}`;
      }
      case ResourceType.file: {
        const file = result as FileResource;

        return `/file/${file.name}?${logParams}`;
      }
      case ResourceType.data_provider: {
        const provider = result as DataProviderResource;

        return `/provider/${provider.name}?${logParams}`;
      }
      default:
        return '';
    }
  };

  getSuggestedResultIconClass = (
    resourceType: ResourceType,
    result: Resource
  ): string => {
    let source = '';

    switch (resourceType) {
      case ResourceType.dashboard: {
        const dashboard = result as DashboardResource;

        return getSourceIconClass(dashboard.product, resourceType);
      }

      case ResourceType.feature: {
        const feature = result as FeatureResource;

        if (feature.availability) {
          source =
            feature.availability.length > 0 ? feature.availability[0] : '';
        }

        return getSourceIconClass(source, resourceType);
      }
      case ResourceType.table: {
        const table = result as TableResource;

        return getSourceIconClass(table.database, resourceType);
      }
      case ResourceType.user: {
        return CONSTANTS.USER_ICON_CLASS;
      }
      case ResourceType.file: {
        const file = result as FileResource;

        return getSourceIconClass(file.type, resourceType);
      }
      case ResourceType.data_provider: {
        const provider = result as DataProviderResource;

        return getSourceIconClass(provider.type, resourceType);
      }
      default:
        return '';
    }
  };

  getSuggestedResultSubTitle = (
    resourceType: ResourceType,
    result: Resource
  ): string => {
    switch (resourceType) {
      case ResourceType.dashboard: {
        const dashboard = result as DashboardResource;

        return dashboard.description;
      }
      case ResourceType.feature: {
        const feature = result as FeatureResource;

        return feature.description;
      }
      case ResourceType.table: {
        const table = result as TableResource;

        return table.description;
      }
      case ResourceType.user: {
        const user = result as UserResource;

        return user.team_name;
      }
      case ResourceType.file: {
        const file = result as FileResource;

        return file.name;
      }
      case ResourceType.user: {
        const provider = result as DataProviderResource;

        return provider.name;
      }
      default:
        return '';
    }
  };

  getSuggestedResultTitle = (
    resourceType: ResourceType,
    result: Resource
  ): React.ReactNode => {
    switch (resourceType) {
      case ResourceType.dashboard: {
        const dashboard = result as DashboardResource;

        return (
          <div className="dashboard-title">
            <div className="text-title-w2 dashboard-name">{dashboard.name}</div>
            <div className="text-title-w2 dashboard-group truncated">
              {dashboard.group_name}
            </div>
          </div>
        );
      }
      case ResourceType.feature: {
        const feature = result as FeatureResource;

        return (
          <div className="text-title-w2 truncated">
            {`${feature.feature_group}.${feature.name}`}
          </div>
        );
      }
      case ResourceType.table: {
        const table = result as TableResource;

        return (
          <div className="text-title-w2 truncated">{`${table.schema}.${table.name}`}</div>
        );
      }
      case ResourceType.user: {
        const user = result as UserResource;

        return (
          <div className="text-title-w2 truncated">{user.display_name}</div>
        );
      }
      case ResourceType.file: {
        const file = result as FileResource;

        return (
          <div className="text-title-w2 truncated">{file.name}</div>
        );
      }
      case ResourceType.data_provider: {
        const provider = result as DataProviderResource;

        return (
          <div className="text-title-w2 truncated">{provider.name}</div>
        );
      }
      default:
        return <div className="text-title-w2 truncated" />;
    }
  };

  getSuggestedResultType = (
    resourceType: ResourceType,
    result: Resource
  ): string => {
    let source = '';

    switch (resourceType) {
      case ResourceType.dashboard: {
        const dashboard = result as DashboardResource;

        return getSourceDisplayName(dashboard.product, resourceType);
      }
      case ResourceType.feature: {
        const feature = result as FeatureResource;

        if (feature.availability) {
          source =
            feature.availability.length > 0 ? feature.availability[0] : '';
        }

        return getSourceDisplayName(source, resourceType);
      }
      case ResourceType.table: {
        const table = result as TableResource;

        return getSourceDisplayName(table.database, resourceType);
      }
      case ResourceType.user:
        return CONSTANTS.PEOPLE_USER_TYPE;
      case ResourceType.file:
        return CONSTANTS.PEOPLE_USER_TYPE;
      case ResourceType.data_provider: {
        const data_provider = result as DataProviderResource;

        return getSourceDisplayName(data_provider.name, resourceType);
      }
      default:
        return '';
    }
  };

  renderResultsByResource = (resourceType: ResourceType) => {
    const suggestedResults = this.getSuggestedResultsForResource(resourceType);

    if (suggestedResults.length === 0) {
      return null;
    }

    const { onItemSelect, searchTerm } = this.props;

    return (
      <div className="inline-results-section">
        <ResultItemList
          onItemSelect={onItemSelect}
          resourceType={resourceType}
          searchTerm={searchTerm}
          suggestedResults={suggestedResults}
          totalResults={this.getTotalResultsForResource(resourceType)}
          title={this.getTitleForResource(resourceType)}
        />
      </div>
    );
  };

  renderResults = () => {
    const { isLoading } = this.props;

    if (isLoading) {
      return null;
    }

    return (
      <>
        {this.renderResultsByResource(ResourceType.table)}
        {indexDashboardsEnabled() &&
          this.renderResultsByResource(ResourceType.dashboard)}
        {indexFeaturesEnabled() &&
          this.renderResultsByResource(ResourceType.feature)}
        {indexUsersEnabled() && this.renderResultsByResource(ResourceType.user)}
        {indexFilesEnabled() && this.renderResultsByResource(ResourceType.file)}
        {indexProvidersEnabled() && this.renderResultsByResource(ResourceType.data_provider)}
      </>
    );
  };

  render() {
    const { className = '', onItemSelect, searchTerm } = this.props;

    return (
      <div id="inline-results" className={`inline-results ${className}`}>
        <div className="inline-results-section search-item-section">
          <SearchItemList onItemSelect={onItemSelect} searchTerm={searchTerm} />
        </div>
        {this.renderResults()}
      </div>
    );
  }
}

export const mapStateToProps = (state: GlobalState) => {
  const { isLoading, dashboards, features, tables, users, files, providers } =
    state.search.inlineResults;

  return {
    isLoading,
    dashboards,
    features,
    tables,
    users,
    files,
    providers,
  };
};

export default connect<StateFromProps, OwnProps>(mapStateToProps)(
  InlineSearchResults
);
