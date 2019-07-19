import * as React from 'react';
import * as DocumentTitle from 'react-document-title';

import TagsList from 'components/common/TagsList';

export class BrowsePage extends React.Component {
  render() {
    return (
      <DocumentTitle title="Browse - Amundsen">
        <div className="container">
          <div className="row">
            <div className="col-xs-12">
              <h3 id="browse-header">Browse Tags</h3>	
              <hr className="header-hr"/>	
              <TagsList />
            </div>
          </div>
        </div>
      </DocumentTitle>
    );
  }
}

export default BrowsePage;
