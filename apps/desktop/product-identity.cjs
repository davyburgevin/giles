// Giles keeps the upstream Python API names while owning its OS identity.
'use strict'
const product = require('../../giles.json')
module.exports = Object.freeze({
  store: false,
  light: false,
  displayName: product.name,
  appId: product.appId,
  channel: 'latest',
  appNamePascal: product.name,
  artifactNamePascal: product.name,
  windowsExecutableName: product.name,
  cliName: 'giles',
  msixAppIdWithOrg: 'DavyBurgevin.Giles'
})
