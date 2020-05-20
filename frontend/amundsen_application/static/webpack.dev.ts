import merge from 'webpack-merge';
import {BundleAnalyzerPlugin} from 'webpack-bundle-analyzer';

import commonConfig from './webpack.common';

export default merge(commonConfig, {
  plugins: [
    // new BundleAnalyzerPlugin()     // Uncomment to check the bundle size on dev
  ],
});
