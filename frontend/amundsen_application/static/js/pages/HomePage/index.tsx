// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

import { resetSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateReset } from 'ducks/search/types';

import MyBookmarks from 'features/MyBookmarksWidget';
import Breadcrumb from 'features/BreadcrumbWidget';
import PopularTables from 'features/PopularResourcesWidget';
import SearchBar from 'features/SearchBarWidget';
import TagsListContainer from 'features/TagsWidget';
import Announcements from 'features/AnnouncementsWidget';
import BadgesListContainer from 'features/BadgesWidget';

import { announcementsEnabled } from 'config/config-utils';

import { SEARCH_BREADCRUMB_TEXT, HOMEPAGE_TITLE } from './constants';

import './styles.scss';

export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type Widget = { // TODO: What file does the Widget type belong in?
  name: string;
  options: {
    path: '/';
  };
};

export type HomePageLayout = Widget[];

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;



export class HomePage extends React.Component<HomePageProps> {
  componentDidMount() {
    this.props.searchReset();
  }

  getHomePageWidgets (): React.ReactNode[] {
  // getHomePageWidgets (layout: HomePageLayout): React.ReactNode[] {
    // TODO: If not configured, default to returning what the homepage previously had,
    // for backwards compatibililty

    // TODO DRY out. Typing the same className every time, redundant do-nothing divs?, etc. 
    return [
      <div className="home-element-container"><SearchBar /></div>,
      <div className="filter-breadcrumb pull-right">
        <Breadcrumb
        direction="right"
        path="/search"
        text={SEARCH_BREADCRUMB_TEXT}
        />
      </div>,
      <div className="home-element-container">
          <BadgesListContainer shortBadgesList />
      </div>,
      <div className="home-element-container">
        <TagsListContainer shortTagsList />
      </div>,
      <div className="home-element-container">
        <MyBookmarks />
      </div>,
      <div className="home-element-container">
        <PopularTables />
      </div>
      // Announcements,  // TODO see only logic about `AnouncementsEnabled() &&`
    ]
  }

  dummyTestLayout = [
    {
      name: 'fakeWidget',
      options: {},
    }
  ]

  homePageWidgets = this.getHomePageWidgets()

// TODO try having widgets getter return the whole div that starts with the 
// announcmentsEnabled() ternary operator clause

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
