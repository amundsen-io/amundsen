// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';

import { resetSearchState } from 'ducks/search/reducer';
import { UpdateSearchStateReset } from 'ducks/search/types';

import Announcements from 'features/AnnouncementsWidget';

import { announcementsEnabled, bookmarksEnabled, getHomePageWidgets } from 'config/config-utils';

import { HomePageWidgetsConfig } from 'config/config-types';
import { HOMEPAGE_TITLE } from './constants';

import './styles.scss';

export interface DispatchFromProps {
  searchReset: () => UpdateSearchStateReset;
}

export type HomePageProps = DispatchFromProps & RouteComponentProps<any>;

const getHomePageWidgetComponents = (
  layout: HomePageWidgetsConfig
): React.ReactNode[] =>
  /* Imports each widget based on its path and puts the widget component's
  JSX into the output array. */

  layout.widgets.map((widget) => {
    const WidgetComponent = React.lazy(
      () =>
        import('/js/features/HomePageWidgets/' + widget.options.path + '.tsx')
    );

    const additionalProps = widget.options.additionalProps
      ? widget.options.additionalProps
      : null;

    return (
      <div className="home-element-container">
        <React.Suspense fallback={<div>Loading...</div>}>
          <WidgetComponent {...additionalProps} />
        </React.Suspense>
      </div>
    );
  });

export const HomePageWidgets = (props) => {
  const { homePageLayout } = props;

  return <div>{getHomePageWidgetComponents(homePageLayout)}</div>;
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
      <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": "https://discover.cmdrvl.com/",
        "name": "Data Discovery Platform",
        "description": "Discover datasets and browse metadata curated by CMD+RVL. Mastery of metadata leads to mastery of getting value out of data.",
        "publisher": {
            "@type": "Corporation",
            "@id": "https://cmdrvl.com#corp",
            "url": "https://cmdrvl.com/",
            "sameAs": "https://cmdrvl.com/company/overview/about-cmdrvl/"
        },
        "author" : {"@id": "https://cmdrvl.com#corp" },
        "audience": "Investors and Analysts in CMBS and Auto Loan asset backed securities."
      } 
      </script>
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
