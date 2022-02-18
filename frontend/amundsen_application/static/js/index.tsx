// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import 'core-js/stable';

import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as ReduxPromise from 'redux-promise';
import createSagaMiddleware from 'redux-saga';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import { Router, Route, Switch } from 'react-router-dom';
import DocumentTitle from 'react-document-title';

import { getDocumentTitle } from 'config/config-utils';

import { analyticsMiddleware } from 'ducks/middlewares';

import { BrowserHistory } from 'utils/navigationUtils';

import { pageViewed } from 'ducks/ui';
import rootReducer from 'ducks/rootReducer';
import rootSaga from 'ducks/rootSaga';
import { createUser } from 'ducks/user/reducer';
import { getBookmarks } from 'ducks/bookmark/reducer';

import {
  PublicClientApplication,
  EventType,
  EventMessage,
  AuthenticationResult,
  InteractionType,
} from '@azure/msal-browser';
import { MsalProvider, MsalAuthenticationTemplate } from '@azure/msal-react';
import { RouteGuard } from './components/RouteGuard';

import AnnouncementPage from './pages/AnnouncementPage';
import BrowsePage from './pages/BrowsePage';
import DashboardPage from './pages/DashboardPage';
import FeaturePage from './pages/FeaturePage';
import HomePage from './pages/HomePage';
import NotFoundPage from './pages/NotFoundPage';
import SearchPage from './pages/SearchPage';
import ProfilePage from './pages/ProfilePage';
import TableDetail from './pages/TableDetailPage';
import LineagePage from './pages/LineagePage';
import ShimmeringDashboardLoader from './pages/DashboardPage/ShimmeringDashboardLoader';

import Preloader from './components/Preloader';
import Footer from './features/Footer';
import NavBar from './features/NavBar';

// MSAL imports
import { msalConfig, loginRequest, securityGroups } from './authConfig';

const authRequest = {
  ...loginRequest,
};

export const msalInstance = new PublicClientApplication(msalConfig);

// Account selection logic is app dependent. Adjust as needed for different use cases.
const accounts = msalInstance.getAllAccounts();
if (accounts.length > 0) {
  msalInstance.setActiveAccount(accounts[0]);
}

const sagaMiddleware = createSagaMiddleware();
const createStoreWithMiddleware = applyMiddleware(
  ReduxPromise,
  analyticsMiddleware,
  sagaMiddleware
)(createStore);
const store = createStoreWithMiddleware(rootReducer);

msalInstance.addEventCallback((event: EventMessage) => {
  if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
    const payload = event.payload as AuthenticationResult;
    const { account } = payload;
    if (account) {
      const user = {
        last_login: new Date().toUTCString(),
        name: account.name,
        mail: account.username,
        id: account.localAccountId,
      };
      store.dispatch(createUser(user));
      store.dispatch(getBookmarks(account.username));
    }

    msalInstance.setActiveAccount(account);
  }
});

sagaMiddleware.run(rootSaga);

const Routes: React.FC = () => {
  const history = BrowserHistory;

  function trackPageView() {
    store.dispatch(pageViewed(window.location.pathname));
  }

  React.useEffect(() => {
    trackPageView(); // To track the first pageview upon load
    history.listen(trackPageView); // To track the subsequent pageviews
  }, [history]);

  return (
    <>
      <Route component={NavBar} />
      <Switch>
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/announcements"
          Component={AnnouncementPage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/browse"
          Component={BrowsePage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/dashboard/:uri"
          Component={DashboardPage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/feature/:group/:name/:version"
          Component={FeaturePage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/search"
          Component={SearchPage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/table_detail/:cluster/:database/:schema/:table"
          Component={TableDetail}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/lineage/:resource/:cluster/:database/:schema/:table"
          Component={LineagePage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/user/:userId"
          Component={ProfilePage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/404"
          Component={NotFoundPage}
        />
        <RouteGuard
          groups={[securityGroups.GroupMember, securityGroups.GroupAdmin]}
          path="/"
          Component={HomePage}
        />
      </Switch>
    </>
  );
};

ReactDOM.render(
  <DocumentTitle title={getDocumentTitle()}>
    <Provider store={store}>
      <Router history={BrowserHistory}>
        <MsalProvider instance={msalInstance}>
          <MsalAuthenticationTemplate
            interactionType={InteractionType.Redirect}
            authenticationRequest={authRequest}
            errorComponent={NotFoundPage}
            loadingComponent={ShimmeringDashboardLoader}
          >
            <div id="main">
              <Preloader />
              <Routes />
              <Footer />
            </div>
          </MsalAuthenticationTemplate>
        </MsalProvider>
      </Router>
    </Provider>
  </DocumentTitle>,
  document.getElementById('content') || document.createElement('div')
);
