// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

import { resetSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateReset } from 'ducks/search/types';

import Announcements from 'features/AnnouncementsWidget';

import { announcementsEnabled, getHomePageWidgets } from 'config/config-utils';
import { Widget } from 'interfaces/Widgets';

import { HOMEPAGE_TITLE } from './constants';

import './styles.scss';
import { HomePageWidgetsConfig } from 'config/config-types';

export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

const getHomePageWidgetComponents = (layout: HomePageWidgetsConfig): React.ReactNode[] => {
  /* Looks up each Widget in layout by its name property, and if found, 
  puts the relevant component's JSX into the output array. */

  const res: React.ReactNode[] = [];

  layout.widgets.forEach((widget) => {
  
    const WidgetComponent = React.lazy(
      () =>
        import('/js/features/HomePageWidgets/' + widget.options.path + '.tsx')
    );

    res.push(
      <div className="home-element-container">
        <React.Suspense fallback={<div>Loading...</div>}>
          <WidgetComponent />
        </React.Suspense>
      </div>
    );
  });

  return res;
};

// const defaultHomePageWidgetsConfig: HomePageWidgetsConfig = { // Move into config-defaults.ts
//   widgets: [
//     {
//       name: 'SearchBarWidget',
//       options: {
//         path: 'SearchBarWidget/index',
//       },
//     },
//     {
//       name: 'BadgesListWidget',
//       options: {
//         path: 'BadgesWidget/index',
//       },
//     },
//     {
//       name: 'TagsListWidget',
//       options: {
//         path: 'TagsListWidget/index',
//       },
//     },
//     {
//       name: 'MyBookmarksWidget',
//       options: {
//         path: 'MyBookmarksWidget/index',
//       },
//     },
//     {
//       name: 'PopularResourcesWidget',
//       options: {
//         path: 'PopularResourcesWidget/index',
//       },
//     },
//   ]

// }


const HomePageWidgets = (props) => {
  const { homePageLayout } = props;
  const widgets = getHomePageWidgetComponents(homePageLayout);

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
            <HomePageWidgets homePageLayout={getHomePageWidgets()} />
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
