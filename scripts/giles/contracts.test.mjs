import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import path from 'node:path'
import test from 'node:test'
import { platformDefaultHermesHome, resolveDesktopHermesHome } from '../../apps/desktop/electron/data-paths.mjs'
const require = createRequire(import.meta.url)
const identity = require('../../apps/desktop/product-identity.cjs')
test('Giles cannot collide with the original desktop or CLI identity', () => {
  assert.equal(identity.displayName, 'Giles')
  assert.equal(identity.appId, 'fr.davyburgevin.giles')
  assert.equal(identity.cliName, 'giles')
  assert.equal(identity.channel, 'latest')
})
test('a fresh Mac has independent data and preserves explicitly selected profiles', () => {
  assert.equal(platformDefaultHermesHome('/Users/test', {}, 'darwin'), '/Users/test/.giles')
  assert.equal(resolveDesktopHermesHome({home:'/Users/test',env:{},platform:'darwin'}), '/Users/test/.giles')
  assert.equal(resolveDesktopHermesHome({home:'/Users/test',env:{HERMES_HOME:'/tmp/giles/profiles/personal'},platform:'darwin'}), '/tmp/giles')
})
