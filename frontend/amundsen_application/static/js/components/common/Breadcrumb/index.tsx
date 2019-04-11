import * as React from 'react';
import { Link } from 'react-router-dom';

import './styles.scss';

interface BreadcrumbProps {
  path: string;
  text: string;
}

const Breadcrumb: React.SFC<BreadcrumbProps> = ({ path, text }) => {
  return (
    <div className="amundsen-breadcrumb">
      <Link to={path}>
        <button className='btn btn-flat-icon'>
          <img className='icon icon-left'/>
          <span>{text}</span>
        </button>
      </Link>
    </div>
  );
};

Breadcrumb.defaultProps = {
  path: '/',
  text: 'Home',
};

export default Breadcrumb;
