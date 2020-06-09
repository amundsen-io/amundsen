import merge from 'webpack-merge';
import commonConfig from './webpack.common';
import TerserPlugin from 'terser-webpack-plugin';

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
});
