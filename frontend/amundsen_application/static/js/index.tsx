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

import { BrowserHistory } from 'utils/navigationUtils';

import DashboardPage from './pages/DashboardPage';
import AnnouncementPage from './pages/AnnouncementPage';
import BrowsePage from './pages/BrowsePage';
import HomePage from './pages/HomePage';
import NotFoundPage from './pages/NotFoundPage';
import SearchPage from './pages/SearchPage';
import ProfilePage from './pages/ProfilePage';
import TableDetail from './pages/TableDetailPage';

import Preloader from './components/common/Preloader';
import Footer from './components/Footer';
import NavBar from './components/NavBar';

import rootReducer from './ducks/rootReducer';
import rootSaga from './ducks/rootSaga';

const sagaMiddleware = createSagaMiddleware();
const createStoreWithMiddleware = applyMiddleware(
  ReduxPromise,
  sagaMiddleware
)(createStore);
const store = createStoreWithMiddleware(rootReducer);

sagaMiddleware.run(rootSaga);

ReactDOM.render(
  <DocumentTitle title="Amundsen - Data Discovery Portal">
    <Provider store={store}>
      <Router history={BrowserHistory}>
        <div id="main">
          <Preloader />
          <Route component={NavBar} />
          <Switch>
            <Route path="/announcements" component={AnnouncementPage} />
            <Route path="/browse" component={BrowsePage} />
            <Route path="/dashboard/:uri" component={DashboardPage} />
            <Route path="/search" component={SearchPage} />
            <Route
              path="/table_detail/:cluster/:database/:schema/:table"
              component={TableDetail}
            />
            <Route path="/user/:userId" component={ProfilePage} />
            <Route path="/404" component={NotFoundPage} />
            <Route path="/" component={HomePage} />
          </Switch>
          <Footer />
        </div>
      </Router>
    </Provider>
  </DocumentTitle>,
  document.getElementById('content') || document.createElement('div')
);
