// Exercise the actual app signer and the designated requirement used by Squirrel.
import assert from 'node:assert/strict'
import { execFileSync, spawnSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import signGiles from '../../apps/desktop/scripts/giles-sign.cjs'

if (process.platform !== 'darwin') throw new Error('Native signing acceptance requires macOS')
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'giles-signing-acceptance-'))
function fixture(name, version) {
  const app = path.join(root, name, 'Giles.app')
  fs.mkdirSync(path.join(app, 'Contents', 'MacOS'), { recursive: true })
  fs.copyFileSync('/usr/bin/true', path.join(app, 'Contents', 'MacOS', 'Giles'))
  fs.writeFileSync(path.join(app, 'Contents', 'Info.plist'), `<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>fr.davyburgevin.giles</string>
<key>CFBundleExecutable</key><string>Giles</string>
<key>CFBundleName</key><string>Giles</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>${version}</string>
</dict></plist>`)
  return app
}
try {
  const installed = fixture('installed', '0.1.0')
  const update = fixture('update', '0.1.1')
  const foreign = fixture('foreign', '0.1.2')
  await signGiles({ app: installed })
  await signGiles({ app: update })
  const descriptor = spawnSync('/usr/bin/codesign', ['-d', '-r-', installed], { encoding: 'utf8', timeout: 60000 })
  assert.equal(descriptor.status, 0)
  const requirement = /designated => (.+)/.exec(descriptor.stdout + '\n' + descriptor.stderr)?.[1]
  assert(requirement, descriptor.stderr)
  execFileSync('/usr/bin/codesign', ['--verify', '--strict', '-R', `=${requirement}`, update], { timeout: 60000 })
  execFileSync('/usr/bin/codesign', ['--force', '--sign', '-', foreign], { timeout: 60000, stdio: 'pipe' })
  const rejected = spawnSync('/usr/bin/codesign', ['--verify', '--strict', '-R', `=${requirement}`, foreign], { timeout: 60000 })
  assert.notEqual(rejected.status, 0, 'A foreign signing identity must not satisfy the installed Giles requirement')
  console.log('Personal signature accepts the next Giles version and rejects a foreign signing identity.')
} finally {
  fs.rmSync(root, { recursive: true, force: true })
}
