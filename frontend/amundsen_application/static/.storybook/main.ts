// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import customWebpackConfig from './webpack.config.js';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';
import webpack from 'webpack';

/**
 * Disables Webpack from splitting the code into chunks
 * @param config - The webpack config to update
 */
function disableChunkSplitting(config) {
  config.optimization = { splitChunks: { chunks: 'async' } };
  config.output = { ...config.output, chunkFilename: '[chunkhash].chunk.js' };
  config.plugins.push(
    new webpack.optimize.LimitChunkCountPlugin({ maxChunks: 1 })
  );

  return config;
}

module.exports = {
  stories: ['../js/**/*.story.tsx'],
  addons: ['@storybook/addon-actions', '@storybook/addon-links'],
  managerWebpack: async (config) => {
    return disableChunkSplitting(config);
  },
  core: {
    builder: 'webpack5',
  },
  staticDirs: ['../../'],
  webpackFinal: (config) => {
    return {
      ...config,
      module: {
        ...config.module,
        rules: customWebpackConfig.module.rules,
      },
      resolve: {
        ...config.resolve,
        ...customWebpackConfig.resolve,
      },
      plugins: [
        new MiniCssExtractPlugin({
          filename: '[name].[contenthash].css',
        }),
        ...config.plugins,
      ],
    };
  },
};
