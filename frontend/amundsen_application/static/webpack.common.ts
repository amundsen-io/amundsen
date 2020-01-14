import * as path from 'path';
import * as fs from 'fs';
import * as webpack from 'webpack';
import HtmlWebpackPlugin from 'html-webpack-plugin';
import MiniCssExtractPlugin from 'mini-css-extract-plugin';

import appConfig from './js/config/config';

const walkSync = (dir, filelist = []) => {
  fs.readdirSync(dir).forEach(file => {
    filelist = fs.statSync(path.join(dir, file)).isDirectory()
      ? walkSync(path.join(dir, file), filelist)
      : filelist.concat(path.join(dir, file));
  });
  return filelist;
};
const templatesList = walkSync('templates');
const htmlWebpackPluginConfig = templatesList.map(file => {
  return new HtmlWebpackPlugin({
      filename: file,
      template: file,
      config: appConfig,
      inject: false,
    });
});

const config: webpack.Configuration = {
    entry: {
      main: ['@babel/polyfill', path.join(__dirname, '/css/styles.scss'), path.join(__dirname, '/js/index.tsx')],
    },
    output: {
        path: path.join(__dirname, '/dist'),
        filename: '[name].js',
    },
    devtool: 'source-map',
    resolve: {
        alias: {
            components: path.join(__dirname, '/js/components'),
            config: path.join(__dirname, '/js/config'),
            ducks: path.join(__dirname, '/js/ducks'),
            interfaces: path.join(__dirname, '/js/interfaces'),
            utils: path.join(__dirname, '/js/utils'),
        },
        extensions: ['.tsx', '.ts', '.js', '.jsx', '.css', '.scss'],
    },
    module: {
      rules: [
        {
          test: /\.ts|\.tsx$/,
          loader: 'ts-loader',
        },
        {
          test: /\.jsx?$/,
          exclude: /node_modules/,
          use: 'babel-loader',
        },
        {
          test: /\.(sa|sc|c)ss$/,
          use: [MiniCssExtractPlugin.loader, 'css-loader', {
            loader: 'sass-loader',
            options: {
              includePaths: [path.join(__dirname, '/css/')]
            }
          }],
        },
        {
          test: /\.(png|svg|jpg|gif)$/,
          use: 'file-loader',
        },
      ],
    },
    plugins: [
      new MiniCssExtractPlugin(),
      ...htmlWebpackPluginConfig,
    ],
    optimization: {
      splitChunks: {
        cacheGroups: {
          default: false,
          major: {
            name: 'vendors',
            test: /[\\/]node_modules[\\/](react|react-dom)[\\/]/,
            chunks: 'all',
          },
        },
      },
    },
};
export default config;
