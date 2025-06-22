$nextCfg = @"
const path = require('path');

module.exports = {
  reactStrictMode: true,
  webpack: (config) => {
    // allow   import ... from "@recallhero/shared"
    config.resolve.alias['@recallhero/shared'] =
      path.resolve(__dirname, '..', 'shared');
    return config;
  },
};
"@

Set-Content -Path .\frontend\next.config.js -Value $nextCfg -Encoding utf8
Write-Host "✅  frontend/next.config.js written."
