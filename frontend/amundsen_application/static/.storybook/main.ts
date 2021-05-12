// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import customWebpackConfig from './webpack.config.js';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';

module.exports = {
  stories: ['../js/**/*.story.tsx'],
  addons: [
    '@storybook/addon-actions',
    '@storybook/addon-links',
    '@storybook/addon-knobs',
  ],
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
