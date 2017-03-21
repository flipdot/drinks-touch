var path = require('path');
const webpack = require('webpack'); //to access built-in plugins

module.exports = {
    entry: [
        'bootstrap-loader',
        './js/index.js',
    ],
    output: {
        filename: 'dist/bundle.js',
        path: path.resolve(__dirname, 'static/')
    },
    module: {
        loaders: [
            {test: /\.css$/, loaders: ["style-loader", "css-loader"] },
            { test: /\.(woff2?|svg)$/, loader: 'url-loader?limit=10000&emitFile=false' },
            { test: /\.(ttf|eot)$/, loader: 'file-loader?emitFile=false' },
            { test: /bootstrap-sass\/assets\/javascripts\//, loader: 'imports-loader?jQuery=jquery' },
            {test: /\.(js|jsx)$/, use: 'babel-loader'},
        ],
    },
    plugins: [
        //new webpack.optimize.UglifyJsPlugin(),
    ],
};