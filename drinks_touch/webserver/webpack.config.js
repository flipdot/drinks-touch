const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
const devMode = process.env.NODE_ENV !== 'production'

if (devMode) {
    console.log('Running in development.');
} else {
    console.log('Running in production.');
}

module.exports = {
    entry: [
        'bootstrap-loader',
        './js/index.js',
    ],
    plugins: [
        new MiniCssExtractPlugin({
            //filename: devMode ? '[name].css' : '[name].[hash].css',
            filename: '[name].css',
            chunkFilename: devMode ? '[id].css' : '[id].[hash].css',
        })
    ],
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'static/dist/')
    },
    module: {
        rules: [
            { test: /\.(sa|sc|c)ss$/, use: [devMode ? 'style-loader' : MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader', 'sass-loader'] },
            {
                test: /\.m?js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ],
    },
    optimization: {
        minimizer: [
            new UglifyJsPlugin({
                cache: true,
                parallel: true,
                sourceMap: true
            }),
            new OptimizeCSSAssetsPlugin({})
        ]
    },
};