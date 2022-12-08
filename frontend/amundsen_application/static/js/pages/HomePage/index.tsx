// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

import { resetSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateReset } from 'ducks/search/types';

import MyBookmarksWidget from 'features/MyBookmarksWidget';
import Breadcrumb from 'features/BreadcrumbWidget';
import PopularResourcesWidget from 'features/PopularResourcesWidget';
import SearchBarWidget from 'features/SearchBarWidget';
import TagsListWidget from 'features/TagsWidget';
import Announcements from 'features/AnnouncementsWidget';
import BadgesListWidget from 'features/BadgesWidget';

import { announcementsEnabled } from 'config/config-utils';
import { Widget } from 'interfaces/Widgets';

import { SEARCH_BREADCRUMB_TEXT, HOMEPAGE_TITLE } from './constants';

import './styles.scss';

export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type HomePageLayout = Widget[];

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

export class HomePage extends React.Component<HomePageProps> {
  componentDidMount() {
    this.props.searchReset();
  }

  getHomePageWidgets(layout: HomePageLayout): React.ReactNode[] {
    /* TODO: Make 100% sure it returns the pre-existing layout absent a custom config,
    to not break any OSS users' Amundsen implementations */

    return [
      <div className="home-element-container">
        <SearchBarWidget />
      </div>,
      <div className="filter-breadcrumb pull-right">
        <Breadcrumb
          direction="right"
          path="/search"
          text={SEARCH_BREADCRUMB_TEXT}
        />
      </div>,
      <div className="home-element-container">
        <BadgesListWidget shortBadgesList />
      </div>,
      <div className="home-element-container">
        <TagsListWidget shortTagsList />
      </div>,
      <div className="home-element-container">
        <MyBookmarksWidget />
      </div>,
      <div className="home-element-container">
        <PopularResourcesWidget />
      </div>,
    ];
  }

  defaultLayout: HomePageLayout = [];

  homePageWidgets = this.getHomePageWidgets(this.defaultLayout);

  render() {
    /* TODO, just display either popular or curated tags,
    do we want the title to change based on which
    implementation is being used? probably not */
    return (
      <main className="container home-page">
        <div className="row">
          <div
            className={`col-xs-12 ${
              announcementsEnabled() ? 'col-md-8' : 'col-md-offset-1 col-md-10'
            }`}
          >
            <h1 className="sr-only">{HOMEPAGE_TITLE}</h1>
            {this.homePageWidgets}
          </div>
          {announcementsEnabled() && (
            <div className="col-xs-12 col-md-offset-1 col-md-3">
              <Announcements />
            </div>
          )}
        </div>
      </main>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) =>
  bindActionCreators(
    {
      searchReset: () => resetSearchState(),
    },
    dispatch
  );

export default connect<DispatchFromProps>(null, mapDispatchToProps)(HomePage);
