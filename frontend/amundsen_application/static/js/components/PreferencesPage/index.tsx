// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { PreferenceGroup } from './PreferenceGroup';

// TODO: Use css-modules instead of 'import'
import './styles.scss';
import {
  ALL_NOTIFICATIONS_SUBTITLE,
  ALL_NOTIFICATIONS_TITLE,
  ALL_PREFERENCE,
  MINIMUM_NOTIFICATIONS_SUBTITLE,
  MINIMUM_NOTIFICATIONS_TITLE,
  MINIMUM_PREFERENCE,
  NOTIFICATION_PREFERENCES_TITLE,
} from './constants';

// TODO: Implement tests before component is exposed

interface PreferencesPageState {
  selectedPreference: string;
}

export interface DispatchFromProps {}

export type PreferencesPageProps = DispatchFromProps;

export class PreferencesPage extends React.Component<
  PreferencesPageProps,
  PreferencesPageState
> {
  constructor(props) {
    super(props);
    this.changePreference = this.changePreference.bind(this);

    this.state = {
      selectedPreference: ALL_PREFERENCE,
    };
  }

  changePreference = (newPreference) => {
    this.setState({
      selectedPreference: newPreference,
    });
  };

  render() {
    return (
      <div className="container">
        <div className="row">
          <div className="col-xs-12 col-md-offset-1 col-md-10">
            <h1 className="preferences-title">
              {NOTIFICATION_PREFERENCES_TITLE}
            </h1>
            <PreferenceGroup
              onClick={this.changePreference}
              preferenceValue={ALL_PREFERENCE}
              selected={this.state.selectedPreference === ALL_PREFERENCE}
              title={ALL_NOTIFICATIONS_TITLE}
              subtitle={ALL_NOTIFICATIONS_SUBTITLE}
            />
            <PreferenceGroup
              onClick={this.changePreference}
              preferenceValue={MINIMUM_PREFERENCE}
              selected={this.state.selectedPreference === MINIMUM_PREFERENCE}
              title={MINIMUM_NOTIFICATIONS_TITLE}
              subtitle={MINIMUM_NOTIFICATIONS_SUBTITLE}
            />
          </div>
        </div>
      </div>
    );
  }
}

export const mapDispatchToProps = (dispatch: any) => {
  return bindActionCreators({}, dispatch);
};

export default connect<DispatchFromProps>(
  null,
  mapDispatchToProps
)(PreferencesPage);
