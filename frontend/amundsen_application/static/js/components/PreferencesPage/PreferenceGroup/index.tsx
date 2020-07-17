// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

export type PreferenceGroupProps = {
  onClick: (value: string) => any;
  preferenceValue: string;
  selected: boolean;
  title: string;
  subtitle: string;
};

export class PreferenceGroup extends React.Component<PreferenceGroupProps> {
  public static defaultProps: Partial<PreferenceGroupProps> = {
    selected: false,
    title: '',
    subtitle: '',
  };

  onClick = () => {
    this.props.onClick(this.props.preferenceValue);
  };

  // TODO: Consolidate with future common RadioButton component.
  render() {
    return (
      <label className="preference-group" onClick={this.onClick}>
        <input
          defaultChecked={this.props.selected}
          type="radio"
          className="preference-radio"
          name="notification-preference"
        />
        <div className="preference-text">
          <div className="title-2">{this.props.title}</div>
          <div className="body-secondary-3">{this.props.subtitle}</div>
        </div>
      </label>
    );
  }
}

export default PreferenceGroup;
