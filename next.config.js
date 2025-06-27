// next.config.js
const path = require('path')

module.exports = {
  reactStrictMode: true,

  /** Add any other top-level Next options above this */

  webpack: (config) => {
    // ── Map the alias used in source files to the real folder
    config.resolve.alias['@recallhero/shared'] = path.resolve(
      __dirname,
      '../shared'            // ← adjust if your monorepo layout differs
    )

    return config
  }
}
