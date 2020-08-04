import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import merge from 'webpack-merge';
import TerserPlugin from 'terser-webpack-plugin';
import commonConfig from './webpack.common';

export default merge(commonConfig, {
  mode: 'production',
  optimization: {
    // minify code. also use parameters that improve build speed.
    minimizer: [
      new TerserPlugin({
        cache: true,
        parallel: true,
        sourceMap: true,
      }),
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
  ],
});
