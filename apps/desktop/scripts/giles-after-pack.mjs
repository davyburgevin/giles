import path from 'node:path'
import afterPack from './after-pack.mjs'
import signGiles from './giles-sign.cjs'

/** @param {import('app-builder-lib').AfterPackContext} context */
export default async function afterPackGiles(context) {
  if (context.electronPlatformName !== 'darwin') throw new Error('Giles packages macOS only')
  await afterPack(context)
  // electron-builder discovers Apple-issued identities only. Sign explicitly
  // after relocation with the personal certificate, before DMG/ZIP creation.
  await signGiles({ app: path.join(context.appOutDir, 'Giles.app') })
}
