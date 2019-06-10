import * as React from 'react';
import * as Avatar from 'react-avatar';
import { Link } from 'react-router-dom';

import { LoggingParams } from '../types';

import { UserResource } from 'interfaces';
import Flag from 'components/common/Flag';

export interface UserListItemProps {
  user: UserResource;
  logging: LoggingParams;
}

class UserListItem extends React.Component<UserListItemProps, {}> {
  constructor(props) {
    super(props);
  }

  getLink = () => {
    const { user, logging } = this.props;
    return `/user/${user.id}/?index=${logging.index}&source=${logging.source}`;
  };

  render() {
    const { user } = this.props;
    return (
      <li className="list-group-item">
        <Link className="resource-list-item user-list-item" to={ this.getLink() }>
          <Avatar name={ user.name } size={ 24 } round={ true } />
          <div className="content">
            <div className="col-xs-12 col-sm-6">
              <div className="title-2">
                { user.name }
                {
                  !user.active &&
                  <Flag text="Alumni" labelStyle='danger' />
                }
              </div>
              <div className="body-secondary-3">
                { `${user.role} on ${user.team_name}` }
              </div>
            </div>
            <div className="hidden-xs col-sm-6">
              <div className="title-3">Frequently Uses</div>
              <div className="body-secondary-3 truncated">
                { /*TODO Fill this with a real value*/ }
                <label>{ user.title }</label>
              </div>
            </div>
          </div>
          <img className="icon icon-right" />
        </Link>
      </li>
    );
  }
}

export default UserListItem;
