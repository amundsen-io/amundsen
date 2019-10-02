import * as React from 'react';
import moment from 'moment-timezone';

import { Dropdown, MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import { notificationsEnabled } from 'config/config-utils';

import AppConfig from 'config/config';
import ColumnDescEditableText from 'components/TableDetail/ColumnDescEditableText';
import { GlobalState } from 'ducks/rootReducer';
import { logClick } from 'ducks/utilMethods';
import { ToggleRequestAction } from 'ducks/notification/types';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { TableColumn } from 'interfaces';

// TODO: Use css-modules instead of 'import'
import './styles.scss';

interface DispatchFromProps {
  openRequestDescriptionDialog: () => ToggleRequestAction;
}

interface OwnProps {
  data?: TableColumn;
  index: number;
}

export type DetailListItemProps = DispatchFromProps & OwnProps;

interface DetailListItemState {
  isExpanded: boolean;
}

class DetailListItem extends React.Component<DetailListItemProps, DetailListItemState> {
  public static defaultProps: Partial<DetailListItemProps> = {
    data: {} as TableColumn,
    index: null,
  };

  constructor(props) {
    super(props);
    this.state = {
      isExpanded: false
    };
  }

  openRequest = () => {
    this.props.openRequestDescriptionDialog();
  }

  onClick = (e) => {
    if (!this.state.isExpanded) {
      const metadata = this.props.data;
      logClick(e, {
        target_id: `column::${metadata.name}`,
        target_type: 'column stats',
        label: `${metadata.name} ${metadata.type}`,
      });
    }

    this.setState(prevState => ({
      isExpanded: !prevState.isExpanded
    }));
  };

  formatDate = (unixEpochSeconds) => {
    return moment(unixEpochSeconds * 1000).format("MMM DD, YYYY");
  };

  renderColumnType = (columnIndex: number, type: string) => {
    const truncatedTypes: string[] = ['array', 'struct', 'map'];
    let shouldTrucate = false;

    const fullText = type.toLowerCase();
    let text = fullText;

    truncatedTypes.forEach((truncatedType) => {
      if (type.startsWith(truncatedType) && type !== truncatedType) {
        shouldTrucate = true;
        text = `${truncatedType}<...>`;
        return;
      };
    })

    if (shouldTrucate) {
      const popoverHover = (
        <Popover className='column-type-popover' id={`column-type-popover:${columnIndex}`}>
          {fullText}
        </Popover>
      );
      const stopPropagation = (event) => {
        event.stopPropagation();
      }
      return (
        <OverlayTrigger
          trigger={['click']}
          placement='right'
          overlay={popoverHover}
          rootClose={true}>
            <a className='column-type'
               href="JavaScript:void(0)"
               onClick={ stopPropagation }
            >
              {text}
            </a>
        </OverlayTrigger>
      )
    }
    return (<div className='column-type'>{text}</div>);
  };

  render() {
    const metadata = this.props.data;
    const isExpandable = metadata.stats && metadata.stats.length > 0;

    const startEpoch = Math.min(...metadata.stats.map(s => parseInt(s.start_epoch, 10)));
    const endEpoch = Math.max(...metadata.stats.map(s => parseInt(s.end_epoch, 10)));
    const startDate = isExpandable ? this.formatDate(startEpoch) : null;
    const endDate = isExpandable ? this.formatDate(endEpoch) : null;

    let infoText = 'Stats reflect data collected';
    if (startDate && endDate) {
      if (startDate === endDate) {
        infoText = `${infoText} on ${startDate} only. (daily partition)`;
      } else {
        infoText = `${infoText} between ${startDate} and ${endDate}.`;
      }
    } else {
      infoText = `${infoText} over a recent period of time.`;
    }

    return (
      <li className='list-group-item detail-list-item'>
        <div className={'column-info ' + (isExpandable ? 'expandable' : '')} onClick={ isExpandable? this.onClick : null }>
          <div className='title-section'>
            <div className='title-row'>
              <div className='name title-2'>{metadata.name}</div>
              { this.renderColumnType(this.props.index, metadata.type) }
            </div>
          </div>
          {
            isExpandable &&
            <img className={'icon ' + (this.state.isExpanded ? 'icon-up' : 'icon-down')}/>
          }
        </div>
        <div className='description-container'>
          <div className={'body-secondary-3 description ' + (isExpandable && !this.state.isExpanded ? 'truncated' : '')}>
            <ColumnDescEditableText
              columnIndex={this.props.index}
              editable={metadata.is_editable}
              value={metadata.description}
              maxLength={AppConfig.editableText.columnDescLength}
            />
          </div>
          {
            notificationsEnabled() &&
            <Dropdown id={`detail-list-item-dropdown:${this.props.index}`} pullRight={true}>
              <Dropdown.Toggle noCaret={true} className="dropdown-icon-more">
                <img className="icon icon-more"/>
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <MenuItem onClick={this.openRequest}>Request Column Description</MenuItem>
              </Dropdown.Menu>
            </Dropdown>
          }
        </div>
        {
          this.state.isExpanded &&
          <div className='column-stats'>
            {
              metadata.stats.map(entry =>
                <div className='column-stat' key={entry.stat_type}>
                  <div className='caption'>
                    {entry.stat_type.toUpperCase()}
                  </div>
                  <div className='body-link'>
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

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ openRequestDescriptionDialog } , dispatch);
};

export default connect<{}, DispatchFromProps, OwnProps>(null, mapDispatchToProps)(DetailListItem);
