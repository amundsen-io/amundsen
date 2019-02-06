import * as React from 'react';
import { Link } from 'react-router-dom';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

interface SearchListItemProps {
  title?: string;
  subtitle?: string;
  lastUpdated?: any; // TODO: Investigate typescript Date error when set as 'number'
  params?: SearchListItemParams;
  schema?: string;
  table?: string;
  db?: string;
  cluster?: string;
}

interface SearchListItemParams {
  source?: string;
  index?: number;
}

const SearchListItem: React.SFC<SearchListItemProps> = ({ title, subtitle, lastUpdated, params, db, schema, table, cluster }) => {

  /* TODO: We have to fix a bug with this feature. Commented out support.
  const createLastUpdatedTimestamp = () => {
    if (lastUpdated) {
      const dateTokens = new Date(lastUpdated).toDateString().split(' ');
      return (
        <label>
          {`${dateTokens[1].toUpperCase()} ${dateTokens[2]}`}
        </label>
      )
    }
    return null;
  }*/

  return (
    <li className="list-group-item search-list-item">
      <Link to={`/table_detail/${cluster}/${db}/${schema}/${table}?index=${params.index}&source=${params.source}`}>
        <img className="icon icon-color icon-database" />
        <div className="resultInfo">
          <span className="title truncated">{ title }</span>
          <span className="subtitle truncated">{ subtitle }</span>
        </div>
        { /*createLastUpdatedTimestamp()*/ }
        <img className="icon icon-right" />
      </Link>
    </li>
  );
};

SearchListItem.defaultProps = {
  title: '',
  subtitle: '',
  params: {},
};

export default SearchListItem;
