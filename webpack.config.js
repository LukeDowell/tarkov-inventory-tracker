const path = require("path");

const config = {
  entry: "./src/app.ts",
  target: "node",
  module: {
    rules: [
      {
        test: /\.(ts|js)?$/,
        loader: 'ts-loader'
      },
    ],
  },
  resolve: {
    extensions: [".ts", ".js"],
  },
  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "bundle.js",
  }
};

module.exports = config
