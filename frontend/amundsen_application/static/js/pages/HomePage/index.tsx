// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

import { resetSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateReset } from 'ducks/search/types';

import MyBookmarks from 'features/MyBookmarks';
import BreadcrumbWidget from 'features/Breadcrumb';
import PopularResources from 'features/PopularResources';
import SearchBarWidget from 'features/SearchBar';
import TagsListContainer from 'features/Tags';
import Announcements from 'features/AnnouncementsWidget';
// import BadgesListWidget from 'features/BadgesWidget';

import { announcementsEnabled } from 'config/config-utils';
import { Widget } from 'interfaces/Widgets';

import { SEARCH_BREADCRUMB_TEXT, HOMEPAGE_TITLE } from './constants';

import  loadable from '@loadable/component'

import './styles.scss';

export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type HomePageLayout = Widget[];

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

const getHomePageWidgets = (layout: HomePageLayout): React.ReactNode[] => {
  /* Looks up each Widget in layout by its name property, and if found, 
  puts the relevant component's JSX into the output array. */

  const res: React.ReactNode[] = [];

  // TODO: Actually need the Suspense thing?

  layout.forEach((widget) => {
    console.log(`widget = ${JSON.stringify(widget)}`)
    // const fileString = `${__dirname}/${widget.options.path}`
    // const fileString = `js/${widget.options.path}`

    // const fileString = () => `${__dirname}/${widget.options.path}`
    const fileString = () => widget.options.path
    // const WidgetComponent = await import(widget.options.path)
    // const WidgetComponentModule = async () => {
    //   await import(widget.options.path)
    // }
    // const WidgetComponent = WidgetComponentModule()
    // const WidgetComponent = React.lazy(() => import(fileString()));
    // const WidgetComponent = React.lazy(() => import('features/Badges/BadgesWidget/index'))

    const WidgetComponent = React.lazy(
      () => import('/js/features/HomePageWidgets/' + widget.options.path + '.tsx')
    );

    // const WidgetComponent = loadable(() => import(fileString()))
    // const WidgetComponent = loadable(() => import('features/Badges/BadgesWidget/index'))
    // const WidgetComponent = loadable((widget) => import(widget.options.path), {
    //   fallback: <div>Fallback from Loadable</div>
    // });

    // console.log(` fileString() = ${fileString()}`);
    // const WidgetComponent = React.lazy(() => import(fileString));
    // const someVariable = 'Badges'
    // const WidgetComponent = React.lazy(() => import(`features/BadgesWidget/index`));
    // const WidgetComponent = React.lazy(() => import(`${__dirname}/${widget.options.path}`));
    // const WidgetComponent = React.lazy(() => import(`${widget.options.path}`));
    // const WidgetComponent = import('features/BadgesWidget/index')
    // const WidgetComponent = React.lazy(() => import('features/CodeBlock/index'));
    // const pathString = 'features/Badges/BadgesWidget/index';
    // console.log(`pathString === 'features/Badges/BadgesWidget/index': ${pathString === 'features/Badges/BadgesWidget/index'}`)
    // const WidgetComponent = React.lazy(() => import(pathString));

    
    
    console.log(`WidgetComponent = ${JSON.stringify(WidgetComponent)}`)
    res.push(
      <div className="home-element-container">
            <React.Suspense fallback={<div>Loading...</div>}>
            <WidgetComponent />
    </React.Suspense>

      </div>
    );
  });


  // layout.forEach((widget) => {
  //   switch (widget.name) {
  //     // TODO should probably look up the string names via an enum?
  //     // TODO the className same for all the widget components?
  //     case 'SearchBarWidget': {
  //       res.push(
  //         <div className="home-element-container">
  //           <SearchBarWidget />
  //         </div>
  //       );
  //       break;
  //     }
  //     // TODO put Breadcrumb inside the search component
  //     case 'BreadcrumbWidget': {
  //       res.push(
  //         <div className="filter-breadcrumb pull-right">
  //           <BreadcrumbWidget
  //             direction="right"
  //             path="/search"
  //             text={SEARCH_BREADCRUMB_TEXT}
  //           />
  //         </div>
  //       );
  //       break;
  //     }
  //     case 'BadgesListWidget': {
  //       res.push(
  //         <div className="home-element-container">
  //           <BadgesListWidget shortBadgesList />
  //         </div>
  //       );
  //       break;
  //     }
  //     case 'TagsListWidget': {
  //       res.push(
  //         <div className="home-element-container">
  //           <TagsListWidget shortTagsList />
  //         </div>
  //       );
  //       break;
  //     }
  //     case 'MyBookmarksWidget': {
  //       res.push(
  //         <div className="home-element-container">
  //           <MyBookmarksWidget />
  //         </div>
  //       );
  //       break;
  //     }
  //     case 'PopularResourcesWidget': {
  //       res.push(
  //         <div className="home-element-container">
  //           <PopularResourcesWidget />
  //         </div>
  //       );
  //       break;
  //     }
  //     default:
  //       console.log(`Widget name not found: ${widget.name}`);
  //   }
  // });

  return res;
};

const defaultHomePageLayout: HomePageLayout = [
  // TODO enums / string constants
  {
    name: 'SearchBarWidget',
    options: {
      path: 'SearchBarWidget/index',
    },
  },
  {
    name: 'BadgesListWidget',
    options: {
      path: 'BadgesWidget/index',
    },
  },
  {
    name: 'TagsListWidget',
    options: {
      path: 'TagsListWidget/index',
    },
  },
  {
    name: 'MyBookmarksWidget',
    options: {
      path: 'MyBookmarksWidget/index',
    },
  },
  {
    name: 'PopularResourcesWidget',
    options: {
      path: 'PopularResourcesWidget/index',
    },
  },
];

const HomePageWidgets = (props) => {
  const { homePageLayout } = props;
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
