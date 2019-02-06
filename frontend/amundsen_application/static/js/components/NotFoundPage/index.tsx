import * as React from 'react';
import * as DocumentTitle from 'react-document-title';

// TODO: Use css-modules instead of 'import'
import './styles.scss';


const NotFoundPage: React.SFC<any> = () => {
  return (
    <DocumentTitle title="404 Page Not Found - Amundsen">
      <div className="not-found-page">
        <h1>404 Page Not Found</h1>
        <span className="glyphicon glyphicon-exclamation-sign" />
      </div>
    </DocumentTitle>
  );
};

export default NotFoundPage;
