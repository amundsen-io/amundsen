// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');

function resolve(dir) {
  return path.join(__dirname, dir);
}

const TSX_PATTERN = /\.ts|\.tsx$/;
const JSX_PATTERN = /\.jsx?$/;
const CSS_PATTERN = /\.(sa|sc|c)ss$/;
const IMAGE_PATTERN = /\.(png|svg|jpg|gif)$/;
const FONT_PATTERN = /\.(ttf|woff2|otf)$/;
const RESOLVED_EXTENSIONS = ['.tsx', '.ts', '.js', '.jsx', '.css', '.scss'];
const PATHS = {
  dist: resolve('../dist'),
  pages: resolve('../js/pages'),
  components: resolve('../js/components'),
  config: resolve('../js/config'),
  ducks: resolve('../js/ducks'),
  interfaces: resolve('../js/interfaces'),
  utils: resolve('../js/utils'),
  css: resolve('../css/'),
};

module.exports = {
  module: {
    rules: [
      {
        test: TSX_PATTERN,
        exclude: /node_modules/,
        loader: 'ts-loader',
      },
      {
        test: JSX_PATTERN,
        exclude: /node_modules/,
        use: 'babel-loader',
      },
      {
        test: CSS_PATTERN,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'sass-loader',
            options: {
              sassOptions: {
                includePaths: [PATHS.css],
              },
            },
          },
        ],
      },
      {
        test: IMAGE_PATTERN,
        use: 'file-loader',
      },
      {
        test: FONT_PATTERN,
        use: 'file-loader',
      },
    ],
  },
  resolve: {
    extensions: RESOLVED_EXTENSIONS,
    alias: {
      pages: PATHS.pages,
      components: PATHS.components,
      config: PATHS.config,
      ducks: PATHS.ducks,
      interfaces: PATHS.interfaces,
      utils: PATHS.utils,
    },
  },
  plugins: [
    // fix "process is not defined" error:
    new webpack.ProvidePlugin({
      process: 'process/browser',
    }),
  ],
};
