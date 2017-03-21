var path = require('path');

module.exports = {
    entry: [
        'bootstrap-loader',
        './js/index.js',
    ],
    output: {
        filename: 'static/dist/bundle.js',
        path: path.resolve(__dirname, '.')
    },
    module: {
        loaders: [
            {test: /\.css$/, loaders: ["style-loader", "css-loader"] },
            { test: /\.(woff2?|svg)$/, loader: 'url-loader?limit=10000' },
            { test: /\.(ttf|eot)$/, loader: 'file-loader' },
            { test: /bootstrap-sass\/assets\/javascripts\//, loader: 'imports-loader?jQuery=jquery' },
        ],
    }
};