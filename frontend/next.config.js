// frontend/next.config.js
const path = require('path')
const withTM = require('next-transpile-modules')([
  // ← pass folder path, not module name
  path.resolve(__dirname, '../shared')
])

module.exports = withTM({
  reactStrictMode: true,
  webpack(config) {
    // still alias imports so TS/JS sees @recallhero/shared
    config.resolve.alias['@recallhero/shared'] = path.resolve(__dirname, '../shared')
    return config
  },
})
