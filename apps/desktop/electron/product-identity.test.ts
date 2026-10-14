import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { test } from 'vitest'

import { applyDesktopIdentity, PRODUCT_IDENTITY } from './product-identity'

test('Giles pins its state before the first single-instance lock', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'giles-identity-'))
  const paths: string[] = []
  const names: string[] = []
  try {
    const name = applyDesktopIdentity({
      getPath: () => root,
      setPath: (_key, value) => paths.push(value),
      setName: value => names.push(value)
    })
    assert.equal(name, 'Giles')
    assert.deepEqual(paths, [path.join(root, 'Giles')])
    assert.deepEqual(names, ['Giles'])
    assert(fs.statSync(paths[0]).isDirectory())
    assert.equal(PRODUCT_IDENTITY.appId, 'fr.davyburgevin.giles')
    assert.equal(PRODUCT_IDENTITY.cliName, 'giles')
  } finally {
    fs.rmSync(root, { recursive: true, force: true })
  }
})
