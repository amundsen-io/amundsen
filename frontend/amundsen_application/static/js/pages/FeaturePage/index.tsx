// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';
import * as ReactMarkdown from 'react-markdown';

import { FeatureMetadata } from 'interfaces/Feature';
import { GlobalState } from 'ducks/rootReducer';
import { getFeature } from 'ducks/feature/reducer';
import { GetFeatureRequest } from 'ducks/feature/types';
import Breadcrumb from 'components/Breadcrumb';
import { getLoggingParams } from 'utils/logUtils';
import { formatDateTimeShort } from 'utils/dateUtils';
import { getSourceDisplayName } from 'config/config-utils';
import { ResourceType } from 'interfaces/Resources';

import './styles.scss';

interface StateFromProps {
  isLoading: boolean;
  statusCode: number | null;
  feature: FeatureMetadata;
}

export interface DispatchFromProps {
  getFeatureDispatch: (
    key: string,
    index: string,
    source: string
  ) => GetFeatureRequest;
}

interface FeatureRouteParams {
  group: string;
  name: string;
  version: string;
}

export type FeaturePageProps = RouteComponentProps<FeatureRouteParams> &
  StateFromProps &
  DispatchFromProps;

export function renderTabs() {
  return null;
}

const FeaturePageLoader: React.FC = () => (
  <div className="resource-detail-layout feature-page">
    <header className="resource-header">
      <section className="header-section">
        <div className="shimmer-page-title is-shimmer-animated" />
        <div className="shimmer-page-subtitle is-shimmer-animated" />
      </section>
    </header>
    <article className="column-layout-1">
      <aside className="left-panel">
        <section className="metadata-section">
          <div className="shimmer-section-title is-shimmer-animated" />
          <div className="shimmer-section-content is-shimmer-animated" />
        </section>
        <section className="column-layout-2">
          <section className="left-panel">
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
          </section>
          <section className="right-panel">
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
            <section className="metadata-section">
              <div className="shimmer-section-title is-shimmer-animated" />
              <div className="shimmer-section-content is-shimmer-animated" />
            </section>
          </section>
        </section>
      </aside>
      <main className="right-panel">
        <section className="metadata-section">
          <div className="shimmer-tab-title">
            <div className="shimmer-tab is-shimmer-animated" />
            <div className="shimmer-tab is-shimmer-animated" />
            <div className="shimmer-tab is-shimmer-animated" />
          </div>
          <div className="shimmer-tab-content is-shimmer-animated" />
          <div className="shimmer-tab-content is-shimmer-animated" />
          <div className="shimmer-tab-content is-shimmer-animated" />
          <div className="shimmer-tab-content is-shimmer-animated" />
          <div className="shimmer-tab-content is-shimmer-animated" />
        </section>
      </main>
    </article>
  </div>
);

const getFeatureKey = (group: string, name: string, version: string) =>
  `${group}/${name}/${version}`;

const FeaturePage: React.FC<FeaturePageProps> = ({
  isLoading,
  feature,
  getFeatureDispatch,
  location,
  match,
}: FeaturePageProps) => {
  const [key, setKey] = React.useState('');
  React.useEffect(() => {
    const { group, name, version } = match.params;
    const newKey = getFeatureKey(group, name, version);
    if (key !== newKey) {
      const { index, source } = getLoggingParams(location.search);
      setKey(newKey);
      getFeatureDispatch(newKey, index, source);
    }
  });

  if (isLoading) {
    return <FeaturePageLoader />;
  }
  const sourcesWithDisplay = feature.availability.map((source) =>
    getSourceDisplayName(source, ResourceType.feature)
  );
  return (
    <div className="resource-detail-layout feature-page">
      <header className="resource-header">
        <section className="header-section">
          <Breadcrumb />
          <span className="icon icon-header icon-database" />
        </section>
        <section className="header-section">
          <h1 className="header-title-text truncated" title={feature.name}>
            {feature.name}
          </h1>
          <div className="text-body-w3">
            Feature &bull;&nbsp;
            {sourcesWithDisplay.join(', ')}
          </div>
        </section>
      </header>
      <article className="column-layout-1">
        <aside className="left-panel">
          <section className="metadata-section">
            <h3 className="section-title text-title-w3">Description</h3>
            <div className="markdown-wrapper">
              <ReactMarkdown>{feature.description}</ReactMarkdown>
            </div>
          </section>
          <section className="column-layout-2">
            <section className="left-panel">
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">Entity</h3>
                {feature.entity}
              </section>
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">Data Type</h3>
                {feature.data_type}
              </section>
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">Source</h3>
                {feature.availability}
              </section>
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">Last Updated</h3>
                <time>
                  {formatDateTimeShort({
                    epochTimestamp: feature.last_updated_timestamp,
                  })}
                </time>
              </section>
            </section>
            <section className="right-panel">
              {feature.partition_column !== null && (
                <section className="metadata-section">
                  <h3 className="section-title text-title-w3">Partition Key</h3>
                  {feature.partition_column}
                </section>
              )}
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">version</h3>
                {feature.version}
              </section>
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">Owners</h3>
                {feature.owners.map((owner) => (
                  <div>{owner.email}</div>
                ))}
              </section>
              <section className="metadata-section">
                <h3 className="section-title text-title-w3">Feature Group</h3>
                {feature.feature_group}
              </section>
            </section>
          </section>
        </aside>
        <main className="right-panel">{renderTabs()}</main>
      </article>
    </div>
  );
};

export const mapStateToProps = (state: GlobalState) => ({
  isLoading: state.feature.isLoading,
  statusCode: state.feature.statusCode,
  feature: state.feature.feature,
});

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators({ getFeatureDispatch: getFeature }, dispatch);

export default connect<StateFromProps, DispatchFromProps>(
  mapStateToProps,
  mapDispatchToProps
)(FeaturePage);
