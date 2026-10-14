'use strict'
// One persistent self-signed certificate signs local and CI artifacts. Explicit
// requirements bind updates to that certificate without weakening verification.
const { execFileSync } = require('node:child_process')
const fs = require('node:fs')
const path = require('node:path')
const { pathToFileURL } = require('node:url')

module.exports = async function signGiles(options) {
  const keychain = process.env.GILES_SIGNING_KEYCHAIN
  const fingerprint = process.env.GILES_SIGNING_FINGERPRINT
  if (!keychain || !/^[A-Fa-f0-9]{40}$/.test(fingerprint || '')) {
    throw new Error('Giles requires its persistent self-signed certificate and fingerprint')
  }
  const app = options.app
  const entitlements = path.resolve(__dirname, '../electron/entitlements.mac.plist')
  const inherit = path.resolve(__dirname, '../electron/entitlements.mac.inherit.plist')
  const sign = (file, outer = false) => {
    const args = ['--force', '--sign', fingerprint, '--keychain', keychain,
      '--timestamp=none', '--options', 'runtime', '--entitlements', outer ? entitlements : inherit]
    if (outer) args.push('--requirements', `designated => identifier "fr.davyburgevin.giles" and anchor = H"${fingerprint}"`)
    execFileSync('/usr/bin/codesign', [...args, file], { stdio: 'inherit' })
  }
  const magics = new Set([0xfeedface, 0xcefaedfe, 0xfeedfacf, 0xcffaedfe, 0xcafebabe, 0xbebafeca])
  const visit = directory => {
    for (const item of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, item.name)
      if (item.isSymbolicLink()) continue
      if (item.isDirectory()) {
        visit(file)
        if (/\.(app|framework|xpc)$/.test(item.name)) sign(file)
      } else if (item.isFile()) {
        const fd = fs.openSync(file, 'r')
        const head = Buffer.alloc(4)
        let count
        try { count = fs.readSync(fd, head, 0, 4, 0) } finally { fs.closeSync(fd) }
        if (count === 4 && magics.has(head.readUInt32BE(0))) sign(file)
      }
    }
  }
  visit(app)
  const { rehashPayloadDigests } = await import(pathToFileURL(path.join(__dirname, 'payload-digests.mjs')).href)
  rehashPayloadDigests(path.join(app, 'Contents/Resources/agent-payload'))
  sign(app, true)
  execFileSync('/usr/bin/codesign', ['--verify', '--deep', '--strict', app], { stdio: 'inherit' })
}
