import * as React from 'react';

import ColumnDescEditableText from '../../../../containers/TableDetail/ColumnDescEditableText';

import InfoButton from '../../../common/InfoButton';
import { TableColumn } from '../../types';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

interface DetailListItemProps {
  data?: TableColumn;
  index: number;
}

interface DetailListItemState {
  isExpanded: boolean;
}

class DetailListItem extends React.Component<DetailListItemProps, DetailListItemState> {
  public static defaultProps: DetailListItemProps = {
    data: {} as TableColumn,
    index: null,
  };

  constructor(props) {
    super(props);
    this.state = {
      isExpanded: false
    };
  }

  onClick = () => {
    this.setState(prevState => ({
      isExpanded: !prevState.isExpanded
    }));
  };

  formatDate = (unixEpochTimeValue) => {
    const date = new Date(0);
    date.setSeconds(unixEpochTimeValue);

    /* TODO: Internationalization */
    return date.toLocaleDateString();
  };

  render() {
    const metadata = this.props.data;
    const isExpandable = metadata.stats && metadata.stats.length > 0;

    const startEpoch = Math.min(...metadata.stats.map(s => parseInt(s.start_epoch, 10)));
    const endEpoch = Math.max(...metadata.stats.map(s => parseInt(s.end_epoch, 10)));
    const startDate = isExpandable ? this.formatDate(startEpoch) : null;
    const endDate = isExpandable ? this.formatDate(endEpoch) : null;

    let infoText = 'Stats collected';
    if (startDate && endDate) {
      if (startDate === endDate) {
        infoText = `${infoText} on ${startDate} partition`;
      }
      else {
        infoText = `${infoText} between ${startDate} and ${endDate}`;
      }
    }
    else {
      infoText = `${infoText} over a recent period of time`;
    }

    return (
      <li className='list-group-item detail-list-item'>
        <div className={'column-info ' + (isExpandable ? 'expandable' : '')} onClick={ isExpandable? this.onClick : null }>
          <div style={{ width: '100%', display: 'inline-grid' }}>
            <div className='title'>
              <div className='name'>{metadata.name}</div>
              <div className='type'>{metadata.type || 'null'}</div>
            </div>
          </div>
          {
            isExpandable &&
            <img className={'icon ' + (this.state.isExpanded ? 'icon-up' : 'icon-down')}/>
          }
        </div>
        <div className={'description ' + (this.state.isExpanded ? '' : (isExpandable ? 'truncated' : ''))}>
          <ColumnDescEditableText
            columnIndex={this.props.index}
            editable={metadata.is_editable}
            value={metadata.description}
          />
        </div>
        {
          this.state.isExpanded &&
          <div className='column-stats'>
            {
              metadata.stats.map(entry =>
                <div className='column-stat' key={entry.stat_type}>
                  <div className='title'>
                    {entry.stat_type.toUpperCase()}
                  </div>
                  <div className='content'>
                    {entry.stat_val}
                  </div>
                </div>
              )
            }
            {
             metadata.stats.length > 0 &&
             <div className="stat-collection-info">
              { infoText }
            </div>
            }
          </div>
        }
      </li>
    );
  }
}

export default DetailListItem;
