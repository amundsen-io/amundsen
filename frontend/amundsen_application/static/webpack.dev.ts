import merge from 'webpack-merge';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
// import { BundleAnalyzerPlugin } from 'webpack-bundle-analyzer';

import commonConfig from './webpack.common';

export default merge(commonConfig, {
  mode: 'development',
  devtool: 'inline-source-map',
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].dev.css',
    }),
    // new BundleAnalyzerPlugin()     // Uncomment to check the bundle size on dev
  ],
  output: {
    filename: '[name].dev.js',
  },
});
