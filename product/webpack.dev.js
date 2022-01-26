const baseConfig = require("./webpack.config");
const merge = require("webpack-merge");

module.exports = merge(baseConfig, {
  devtool: "#eval-source-map",
  devServer: {
    hot: true,
    compress: true,
    port: 9000,
    open: true,
  }
});
