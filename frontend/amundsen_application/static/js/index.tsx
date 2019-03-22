import * as React from 'react';
import * as ReactDOM from 'react-dom';
import * as ReduxPromise from 'redux-promise';

import createSagaMiddleware from 'redux-saga';

import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import DocumentTitle from 'react-document-title';

import AnnouncementPage from './components/AnnouncementPage';
import BrowsePage from './components/BrowsePage';
import Feedback from './components/Feedback';
import Footer from './components/Footer';
import NavBar from './components/NavBar';
import NotFoundPage from './components/NotFoundPage';
import SearchPage from './components/SearchPage';
import TableDetail from './components/TableDetail';

import rootReducer from './ducks/rootReducer';
import rootSaga from './ducks/rootSaga';

const sagaMiddleware = createSagaMiddleware();
const createStoreWithMiddleware = applyMiddleware(ReduxPromise, sagaMiddleware)(createStore);
const store = createStoreWithMiddleware(rootReducer);

sagaMiddleware.run(rootSaga);

ReactDOM.render(
  <DocumentTitle title="Amundsen - Data Discovery Portal">
    <Provider store={store}>
      <BrowserRouter>
        <div id="main">
          <NavBar />
          <Switch>
            <Route path="/table_detail/:cluster/:db/:schema/:table" component={TableDetail} />
            <Route path="/announcements" component={AnnouncementPage} />
            <Route path="/browse" component={BrowsePage} />
            <Route path="/search" component={SearchPage} />
            <Route path="/404" component={NotFoundPage} />
            <Route path="/" component={SearchPage} />
          </Switch>
          <Feedback />
          <Footer />
        </div>
      </BrowserRouter>
    </Provider>
  </DocumentTitle>
  , document.getElementById('content') || document.createElement('div'),
);
