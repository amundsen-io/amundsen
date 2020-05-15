import * as React from "react";

import "./styles.scss";

const ShimmeringDashboardLoader: React.FC = () => {
  return (<div className="shimmer-loader">
    <div className="shimmer-loader-row">
      <div className="shimmer-loader-cell double animate" />
      <div className="shimmer-loader-cell simple animate" />
    </div>
    <div className="shimmer-loader-row">
      <div className="shimmer-loader-cell simple animate" />
      <div className="shimmer-loader-cell double animate" />
    </div>
    <div className="shimmer-loader-row">
      <div className="shimmer-loader-cell double animate" />
      <div className="shimmer-loader-cell simple animate" />
    </div>
  </div>);
};

export default ShimmeringDashboardLoader;
