// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import './styles.scss';


interface LoadingSpinnerOverlayProps {
  isLoading: boolean;
}

const LoadingSpinnerOverlay: React.FC<LoadingSpinnerOverlayProps> = ({ isLoading }) => (
  isLoading ? (
    <div className="spinner-overlay">
      <div className="spinner-container">
        {/* Replace with your spinner graphic or CSS animation */}
        {/* <div className="spinner"> */}
          <img
            src="/static/images/loading_spinner.gif"
            alt="loading..."
            className="loading-spinner"
          />
        {/* </div> */}
      </div>
    </div>
  ) : null
);

export default LoadingSpinnerOverlay;
