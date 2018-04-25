const path = require('path')

module.exports = {
  entry: {
    babel_polyfill: 'babel-polyfill',
    main: './src/main.js',
    stuff: './src/stuff.js'
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js'
  },
  module: {
    rules: [
      { test: /\.js$/, exclude: /node_modules/, loader: "babel-loader" }
    ]
  }
}
