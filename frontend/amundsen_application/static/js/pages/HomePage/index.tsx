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
import { COMMENTS_PLACEHOLDER } from 'features/Feedback/constants';

export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type HomePageLayout = Widget[];

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

const getHomePageWidgets = (layout: HomePageLayout): React.ReactNode[] => {
  /* Looks up each Widget in layout by its name property, and if found, 
  puts the relevant component's JSX into the output array. */

  const res: React.ReactNode[] = [];

  layout.forEach((widget) => {
    switch (widget.name) {
      // TODO should probably look up the string names via an enum?
      // TODO the className same for all the widget components?
      case 'SearchBarWidget': {
        res.push(
          <div className="home-element-container">
            <SearchBarWidget />
          </div>
        );
        break;
      }
      // TODO put Breadcrumb inside the search component
      case 'Breadcrumb': {
        res.push(
          <div className="filter-breadcrumb pull-right">
            <Breadcrumb
              direction="right"
              path="/search"
              text={SEARCH_BREADCRUMB_TEXT}
            />
          </div>
        );
        break;
      }
      case 'BadgesListWidget': {
        res.push(
          <div className="home-element-container">
            <BadgesListWidget shortBadgesList />
          </div>
        );
        break;
      }
      case 'TagsListWidget': {
        res.push(
          <div className="home-element-container">
            <TagsListWidget shortTagsList />
          </div>
        );
        break;
      }
      case 'MyBookmarksWidget': {
        res.push(
          <div className="home-element-container">
            <MyBookmarksWidget />
          </div>
        );
        break;
      }
      case 'PopularResourcesWidget': {
        res.push(
          <div className="home-element-container">
            <PopularResourcesWidget />
          </div>
        );
        break;
      }
      default:
        console.log(`Widget name not found: ${widget.name}`);
    }
  });

  return res;
};

const defaultHomePageLayout: HomePageLayout = [
  // TODO enums / string constants
  {
    name: 'SearchBarWidget',
    options: {},
  },
  // TODO breadcrumb into searchbar
  {
    name: 'Breadcrumb',
    options: {},
  },
  {
    name: 'BadgesListWidget',
    options: {},
  },
  {
    name: 'TagsListWidget',
    options: {},
  },
  {
    name: 'MyBookmarksWidget',
    options: {},
  },
  {
    name: 'PopularResourcesWidget',
    options: {},
  },
];

const HomePageWidgets = (props) => {
  const { homePageLayout } = props;
  // TODO for widget in widgets, make a div with the className
  const widgets = getHomePageWidgets(homePageLayout);

  return <div>{widgets}</div>;
};

export class HomePage extends React.Component<HomePageProps> {
  componentDidMount() {
    this.props.searchReset();
  }

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
            <HomePageWidgets homePageLayout={defaultHomePageLayout} />
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
