// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import * as DocumentTitle from 'react-document-title';

import TagsListWidget from 'features/TagsWidget';
import BadgesListWidget from 'features/BadgesWidget';

import { BROWSE_PAGE_DOCUMENT_TITLE } from './constants';

import './styles.scss';

const BrowsePage: React.FC<{}> = () => (
  <>
    <DocumentTitle title={BROWSE_PAGE_DOCUMENT_TITLE}>
      <main className="container">
        <div className="row browse-row">
          <div className="col-xs-12 col-md-10 col-md-offset-1">
            <BadgesListWidget shortBadgesList={false} />
          </div>
        </div>
        <div className="row browse-row">
          <div className="col-xs-12 col-md-10 col-md-offset-1">
            <TagsListWidget shortTagsList={false} />
          </div>
        </div>
      </main>
    </DocumentTitle>
  </>
);

export default BrowsePage;
