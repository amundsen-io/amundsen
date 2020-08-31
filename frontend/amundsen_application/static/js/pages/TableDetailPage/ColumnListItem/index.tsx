// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem } from 'react-bootstrap';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { notificationsEnabled, getMaxLength } from 'config/config-utils';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { OpenRequestAction } from 'ducks/notification/types';
import { logClick } from 'ducks/utilMethods';
import { RequestMetadataType, TableColumn } from 'interfaces';

import './styles.scss';
import EditableSection from 'components/common/EditableSection';
import ColumnStats from '../ColumnStats';
import ColumnDescEditableText from '../ColumnDescEditableText';
import ColumnType from './ColumnType';

const MORE_BUTTON_TEXT = 'More options';
const EDITABLE_SECTION_TITLE = 'Description';

interface DispatchFromProps {
  openRequestDescriptionDialog: (
    requestMetadataType: RequestMetadataType,
    columnName: string
  ) => OpenRequestAction;
}

interface OwnProps {
  data: TableColumn;
  database: string;
  index: number;
  editText: string;
  editUrl: string;
}

interface ColumnListItemState {
  isExpanded: boolean;
}

export type ColumnListItemProps = DispatchFromProps & OwnProps;

export class ColumnListItem extends React.Component<
  ColumnListItemProps,
  ColumnListItemState
> {
  constructor(props) {
    super(props);
    this.state = {
      isExpanded: false,
    };
  }

  toggleExpand = (e) => {
    const { data } = this.props;
    if (!this.state.isExpanded) {
      logClick(e, {
        target_id: `column::${data.name}`,
        target_type: 'column stats',
        label: `${data.name} ${data.col_type}`,
      });
    }
    if (this.shouldRenderDescription() || data.stats.length !== 0) {
      this.setState((prevState) => ({
        isExpanded: !prevState.isExpanded,
      }));
    }
  };

  openRequest = () => {
    this.props.openRequestDescriptionDialog(
      RequestMetadataType.COLUMN_DESCRIPTION,
      this.props.data.name
    );
  };

  stopPropagation = (e) => {
    e.stopPropagation();
  };

  shouldRenderDescription = (): boolean => {
    const { data, editText, editUrl } = this.props;
    if (data.description) {
      return true;
    }
    if (!editText && !editUrl && !data.is_editable) {
      return false;
    }
    return true;
  };

  render() {
    const { data, database } = this.props;
    return (
      <li className="list-group-item clickable" onClick={this.toggleExpand}>
        <div className="column-list-item">
          <section className="column-header">
            <div
              className={`column-details truncated ${
                !this.state.isExpanded ? 'my-auto' : ''
              }`}
            >
              <div className="column-name">{data.name}</div>
              {!this.state.isExpanded && (
                <div className="column-desc body-3 truncated">
                  {data.description}
                </div>
              )}
            </div>
            <div className="resource-type">
              <ColumnType
                columnName={data.name}
                database={database}
                type={data.col_type}
              />
            </div>
            <div className="badges">{/* Placeholder */}</div>
            <div className="actions">
              {
                // TODO - Make this dropdown into a separate component
                notificationsEnabled() && (
                  <Dropdown
                    id={`detail-list-item-dropdown:${this.props.index}`}
                    onClick={this.stopPropagation}
                    pullRight
                    className="column-dropdown"
                  >
                    <Dropdown.Toggle noCaret>
                      <span className="sr-only">{MORE_BUTTON_TEXT}</span>
                      <img className="icon icon-more" alt="" />
                    </Dropdown.Toggle>
                    <Dropdown.Menu>
                      <MenuItem onClick={this.openRequest}>
                        Request Column Description
                      </MenuItem>
                    </Dropdown.Menu>
                  </Dropdown>
                )
              }
            </div>
          </section>
          {this.state.isExpanded && (
            <section className="expanded-content">
              <div className="stop-propagation" onClick={this.stopPropagation}>
                {this.shouldRenderDescription() && (
                  <EditableSection
                    title={EDITABLE_SECTION_TITLE}
                    readOnly={!data.is_editable}
                    editText={this.props.editText}
                    editUrl={this.props.editUrl}
                  >
                    <ColumnDescEditableText
                      columnIndex={this.props.index}
                      editable={data.is_editable}
                      maxLength={getMaxLength('columnDescLength')}
                      value={data.description}
                    />
                  </EditableSection>
                )}
              </div>
              <ColumnStats stats={data.stats} />
            </section>
          )}
        </div>
      </li>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({ openRequestDescriptionDialog }, dispatch);
};

export default connect<{}, DispatchFromProps, OwnProps>(
  null,
  mapDispatchToProps
)(ColumnListItem);
