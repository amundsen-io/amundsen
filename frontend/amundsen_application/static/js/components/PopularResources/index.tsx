// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import { PopularResource, ResourceDict, ResourceType } from 'interfaces';

import InfoButton from 'components/InfoButton';
import PaginatedResourceList from 'components/ResourceList/PaginatedResourceList';
import TabsComponent, { TabInfo } from 'components/TabsComponent';
import ShimmeringResourceLoader from 'components/ShimmeringResourceLoader';
import {
  getDisplayNameByResource,
  indexDashboardsEnabled,
} from 'config/config-utils';

import popularResources, {
  getPopularResources,
} from 'ducks/popularTables/reducer';
import { GetPopularResourcesRequest } from 'ducks/popularTables/types';
import { GlobalState } from 'ducks/rootReducer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import {
  POPULAR_RESOURCES_LABEL,
  POPULAR_RESOURCES_INFO_TEXT,
  POPULAR_RESOURCES_SOURCE_NAME,
  POPULAR_RESOURCES_PER_PAGE,
  EMPTY_POPULAR_RESOURCES_MESSAGE,
} from './constants';

import './styles.scss';

export interface StateFromProps {
  popularResources: ResourceDict<PopularResource[]>;
  isLoaded: boolean;
}

export interface DispatchFromProps {
  getPopularResources: () => GetPopularResourcesRequest;
}

export type PopularResourcesProps = StateFromProps & DispatchFromProps;

export class PopularResources extends React.Component<PopularResourcesProps> {
  componentDidMount() {
    this.props.getPopularResources();
  }

  generateTabContent = (resource: ResourceType): JSX.Element | undefined => {
    const popularResources = this.props.popularResources[resource];

    if (!popularResources) {
      return undefined;
    }

    return (
      <PaginatedResourceList
        allItems={popularResources}
        emptyText={EMPTY_POPULAR_RESOURCES_MESSAGE}
        itemsPerPage={POPULAR_RESOURCES_PER_PAGE}
        source={POPULAR_RESOURCES_SOURCE_NAME}
      />
    );
  };

  generateTabKey = (resource: ResourceType) => `popularresourcetab:${resource}`;

  generateTabTitle = (resource: ResourceType): string => {
    const popularResources = this.props.popularResources[resource];

    if (!popularResources) {
      return '';
    }

    return `${getDisplayNameByResource(resource)} (${popularResources.length})`;
  };

  generateTabInfo = (): TabInfo[] => {
    const tabInfo: TabInfo[] = [];

    tabInfo.push({
      content: this.generateTabContent(ResourceType.table),
      key: this.generateTabKey(ResourceType.table),
      title: this.generateTabTitle(ResourceType.table),
    });

    if (indexDashboardsEnabled()) {
      tabInfo.push({
        content: this.generateTabContent(ResourceType.dashboard),
        key: this.generateTabKey(ResourceType.dashboard),
        title: this.generateTabTitle(ResourceType.dashboard),
      });
    }

    return tabInfo;
  };

  render() {
    const { isLoaded } = this.props;
    let content = (
      <ShimmeringResourceLoader numItems={POPULAR_RESOURCES_PER_PAGE} />
    );

    if (isLoaded) {
      content = (
        <TabsComponent
          tabs={this.generateTabInfo()}
          defaultTab={this.generateTabKey(ResourceType.table)}
        />
      );
    }

    return (
      <article className="popular-table-list">
        <div className="popular-tables-header">
          <h2 className="popular-tables-header-text">
            {POPULAR_RESOURCES_LABEL}
          </h2>
          <InfoButton infoText={POPULAR_RESOURCES_INFO_TEXT} />
        </div>
        {content}
      </article>
    );
  }
}
export const mapStateToProps = (state: GlobalState) => ({
  popularResources: state.popularResources.popularResources,
  isLoaded: state.popularResources.popularResourcesIsLoaded,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getPopularResources }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(PopularResources);
