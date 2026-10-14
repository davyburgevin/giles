import { afterEach, describe, expect, it, vi } from 'vitest'

const { client } = vi.hoisted(() => ({
  client: {
    autoDownload: true,
    autoInstallOnAppQuit: true,
    autoRunAppAfterInstall: false,
    channel: '',
    allowPrerelease: true,
    allowDowngrade: true,
    currentVersion: { version: '9.9.9' },
    on: vi.fn(),
    setFeedURL: vi.fn(),
    checkForUpdates: vi.fn(async () => null)
  }
}))

vi.mock('electron', () => ({ autoUpdater: {} }))
vi.mock('electron-updater', () => ({
  default: {
    MacUpdater: class {
      constructor() {
        return client
      }
    }
  }
}))

import { createMacStrategy } from './mac-client'

afterEach((): void => {
  vi.clearAllMocks()
  client.currentVersion = { version: '9.9.9' }
})

function deps(
  feedBaseUrl = '',
  light = false,
  channel: 'stable' | 'canary' = 'stable'
): Parameters<typeof createMacStrategy>[0] {
  return {
    channel,
    light,
    feedBaseUrl,
    appVersion: '0.28.0',
    log: vi.fn(),
    emitProgress: vi.fn(),
    beforeInstall: vi.fn(),
    onInstallFailure: vi.fn()
  }
}

describe('Giles macOS client wiring', () => {
  it('uses Giles releases and forbids implicit installs, prereleases or downgrades', async () => {
    const strategy = createMacStrategy(deps())
    expect(client.setFeedURL).toHaveBeenCalledExactlyOnceWith({
      provider: 'github', owner: 'davyburgevin', repo: 'giles', channel: 'latest'
    })
    await expect(strategy.check()).rejects.toThrow('not active')
    expect(client.autoDownload).toBe(false)
    expect(client.autoInstallOnAppQuit).toBe(false)
    expect(client.autoRunAppAfterInstall).toBe(true)
    expect(client.allowDowngrade).toBe(false)
    expect(client.channel).toBe('latest')
    expect(client.allowPrerelease).toBe(false)
  })

  it('an inherited upstream feed or channel cannot redirect Giles updates', () => {
    createMacStrategy(deps('https://updates.example/', true, 'canary'))
    expect(client.setFeedURL).toHaveBeenCalledExactlyOnceWith({
      provider: 'github', owner: 'davyburgevin', repo: 'giles', channel: 'latest'
    })
    expect(client.channel).toBe('latest')
    expect(client.allowPrerelease).toBe(false)
  })
})
