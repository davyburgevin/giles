import { autoUpdater as nativeUpdater } from 'electron'
import electronUpdater from 'electron-updater'

import type { ChannelTarget } from './channel'
import { MacStrategy, type MacStrategyDeps, prepareMacInstall } from './mac'

export interface MacClientDeps extends Omit<MacStrategyDeps, 'updater' | 'prepareInstall'> {
  light: boolean
  feedBaseUrl: string
  feed?: { url: string; channel: string }
  log: (message: string) => void
}

export function createChannelMacStrategy(_deps: MacClientDeps, _target: ChannelTarget): MacStrategy {
  throw new Error('Giles updates come only from davyburgevin/giles GitHub releases.')
}

export function createMacStrategy(deps: MacClientDeps): MacStrategy {
  const updater = new electronUpdater.MacUpdater()
  updater.autoDownload = false
  updater.autoInstallOnAppQuit = false
  updater.autoRunAppAfterInstall = true
  updater.channel = 'latest'
  updater.allowPrerelease = false
  updater.allowDowngrade = false
  updater.on('error', error => deps.log(`Giles updater: ${error.message}`))
  updater.setFeedURL({ provider: 'github', owner: 'davyburgevin', repo: 'giles', channel: 'latest' })
  return new MacStrategy({ ...deps, channel: 'latest', updater, prepareInstall: () => prepareMacInstall(nativeUpdater) })
}
