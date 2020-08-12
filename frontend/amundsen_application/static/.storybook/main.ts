import merge from 'webpack-merge';

import devWebpackConfig from '../webpack.dev';

module.exports = {
  stories: ['../js/**/*.story.tsx'],
  addons: ['@storybook/addon-actions', '@storybook/addon-links'],
  webpackFinal: async (config) => {
    return merge(devWebpackConfig, config);
  },
};
