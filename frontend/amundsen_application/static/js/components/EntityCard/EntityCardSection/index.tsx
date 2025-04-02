// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import InfoButton from 'components/InfoButton';

import { IconSizes } from 'interfaces';

import './styles.scss';

export interface EntityCardSectionProps {
  title: string;
  infoText?: string;
  contentRenderer: (readOnly?: boolean) => JSX.Element;
  isEditable: boolean;
}

interface EntityCardSectionState {
  readOnly: boolean;
}

class EntityCardSection extends React.Component<
  EntityCardSectionProps,
  EntityCardSectionState
> {
  private editButton: React.RefObject<HTMLButtonElement>;

  constructor(props) {
    super(props);
    this.state = {
      readOnly: true,
    };

    this.editButton = React.createRef();
    this.toggleEditMode = this.toggleEditMode.bind(this);
  }

  toggleEditMode() {
    const { isEditable } = this.props;
    const { readOnly } = this.state;

    if (isEditable) {
      this.setState({ readOnly: !readOnly });
    }
    this.editButton.current?.blur();
  }

  render() {
    const { readOnly } = this.state;
    const { title, infoText, isEditable, contentRenderer } = this.props;
    const activeButtonClass = readOnly
      ? 'icon edit-button'
      : 'active-edit-button';

    return (
      <div className="entity-card-section">
        <div className="content-header">
          <div id="section-title" className="caption">
            {title.toUpperCase()}
            {infoText && (
              <InfoButton
                infoText={infoText}
                placement="top"
                size={IconSizes.SMALL}
              />
            )}
            {isEditable && (
              <button
                type="button"
                className={`btn ${activeButtonClass}`}
                onClick={this.toggleEditMode}
                ref={this.editButton}
              />
            )}
          </div>
        </div>
        <div id="section-content" className="content">
          {contentRenderer(readOnly)}
        </div>
      </div>
    );
  }
}

export default EntityCardSection;
