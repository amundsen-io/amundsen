// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import './styles.scss';

class LoadingSpinner extends React.Component {
  render() {
    return (
      <img
        src="/static/images/loading_spinner.gif"
        alt="loading..."
        className="loading-spinner"
      />
    );
  }
}

export default LoadingSpinner;
