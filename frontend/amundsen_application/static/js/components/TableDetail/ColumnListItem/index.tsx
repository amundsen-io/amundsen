// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Dropdown, MenuItem, OverlayTrigger, Popover } from 'react-bootstrap';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import ColumnDescEditableText from 'components/TableDetail/ColumnDescEditableText';
import ColumnStats from 'components/TableDetail/ColumnStats';
import { notificationsEnabled, getMaxLength } from 'config/config-utils';
import { openRequestDescriptionDialog } from 'ducks/notification/reducer';
import { OpenRequestAction } from 'ducks/notification/types';
import { logClick } from 'ducks/utilMethods';
import { RequestMetadataType, TableColumn } from 'interfaces';

import './styles.scss';
import EditableSection from 'components/common/EditableSection';

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
    const metadata = this.props.data;
    if (!this.state.isExpanded) {
      logClick(e, {
        target_id: `column::${metadata.name}`,
        target_type: 'column stats',
        label: `${metadata.name} ${metadata.col_type}`,
      });
    }
    if (this.shouldRenderDescription() || metadata.stats.length !== 0) {
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

  renderColumnType = (columnIndex: number, type: string) => {
    const truncatedTypes: string[] = ['array', 'struct', 'map', 'row'];
    let shouldTrucate = false;

    const fullText = type.toLowerCase();
    let text = fullText;

    truncatedTypes.forEach((truncatedType) => {
      if (type.startsWith(truncatedType) && type !== truncatedType) {
        shouldTrucate = true;
        const lastChar = type.charAt(type.length - 1);
        if (lastChar === '>') {
          text = `${truncatedType}<...>`;
        } else if (lastChar === ')') {
          text = `${truncatedType}(...)`;
        } else {
          text = `${truncatedType}...`;
        }
      }
    });

    if (shouldTrucate) {
      const popoverHover = (
        <Popover
          className="column-type-popover"
          id={`column-type-popover:${columnIndex}`}
        >
          {fullText}
        </Popover>
      );
      return (
        <OverlayTrigger
          trigger={['click']}
          placement="left"
          overlay={popoverHover}
          rootClose
        >
          <a
            className="column-type"
            href="JavaScript:void(0)"
            onClick={this.stopPropagation}
          >
            {text}
          </a>
        </OverlayTrigger>
      );
    }
    return <div className="column-type">{text}</div>;
  };

  render() {
    const metadata = this.props.data;
    return (
      <li className="list-group-item clickable" onClick={this.toggleExpand}>
        <div className="column-list-item">
          <section className="column-header">
            <div
              className={`column-details truncated ${
                !this.state.isExpanded ? 'my-auto' : ''
              }`}
            >
              <div className="column-name">{metadata.name}</div>
              {!this.state.isExpanded && (
                <div className="column-desc body-3 truncated">
                  {metadata.description}
                </div>
              )}
            </div>
            <div className="resource-type">
              {this.renderColumnType(this.props.index, metadata.col_type)}
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
                    readOnly={!metadata.is_editable}
                    editText={this.props.editText}
                    editUrl={this.props.editUrl}
                  >
                    <ColumnDescEditableText
                      columnIndex={this.props.index}
                      editable={metadata.is_editable}
                      maxLength={getMaxLength('columnDescLength')}
                      value={metadata.description}
                    />
                  </EditableSection>
                )}
              </div>
              <ColumnStats stats={metadata.stats} />
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
