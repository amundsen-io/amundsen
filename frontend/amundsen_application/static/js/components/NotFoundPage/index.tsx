import * as React from 'react';
import * as DocumentTitle from 'react-document-title';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

import Breadcrumb from 'components/common/Breadcrumb';

const NotFoundPage: React.SFC<any> = () => {
  return (
    <DocumentTitle title="404 Page Not Found - Amundsen">
      <div className="container not-found-page">
        <Breadcrumb path="/" text="Home" />
        <h1>404 Page Not Found</h1>
        <img className="icon icon-alert"/>
      </div>
    </DocumentTitle>
  );
};

export default NotFoundPage;
