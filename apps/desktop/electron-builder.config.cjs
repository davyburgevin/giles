// Giles packages only the native Apple Silicon app and the upstream Python payload.
// @ts-check
'use strict'
const path = require('node:path')
const { displayName, appId, appNamePascal } = require('./product-identity.cjs')
/** @satisfies {import('app-builder-lib').Configuration} */
module.exports = {
  electronVersion: require('./package.json').devDependencies.electron,
  appId,
  productName: displayName,
  executableName: displayName,
  protocols: [{ name: 'Giles Protocol', schemes: ['giles'] }],
  artifactName: 'Giles-${version}-${os}-${arch}.${ext}',
  icon: 'assets/icon.icns',
  publish: [{ provider: 'github', owner: 'davyburgevin', repo: 'giles', channel: 'latest' }],
  extraMetadata: { name: appNamePascal, productName: displayName, desktopName: appId },
  directories: { output: 'release' },
  files: ['dist/**', 'assets/**', 'public/**', 'package.json'],
  beforeBuild: async () => false,
  beforePack: 'scripts/before-pack.mjs',
  afterPack: 'scripts/after-pack.mjs',
  extraResources: [
    { from: 'build/install-stamp.json', to: 'install-stamp.json' },
    { from: 'build/agent-payload', to: 'agent-payload' }
  ],
  asar: { unpack: ['**/*.node', '**/prebuilds/**', 'dist/**'] },
  mac: {
    icon: 'assets/icon.icns',
    notarize: false,
    sign: require('./scripts/giles-sign.cjs'),
    publish: [{ provider: 'github', owner: 'davyburgevin', repo: 'giles', channel: 'latest' }],
    category: 'public.app-category.developer-tools',
    target: [{ target: 'dmg', arch: ['arm64'] }, { target: 'zip', arch: ['arm64'] }],
    extendInfo: {
      CFBundleDisplayName: displayName,
      LSRequiresNativeExecution: true,
      NSMicrophoneUsageDescription: 'Giles uses the microphone when you enable voice input.',
      NSCameraUsageDescription: 'Giles uses the camera when you request it.',
      NSAudioCaptureUsageDescription: 'Giles uses audio capture for voice conversations.',
      NSScreenCaptureUsageDescription: 'Giles captures the screen when you request it.',
      NSAppleEventsUsageDescription: 'Giles automates applications when you request it.',
      NSLocalNetworkUsageDescription: 'Giles connects to local devices when you request it.',
      NSContactsUsageDescription: 'Giles accesses contacts when you request it.',
      NSCalendarsFullAccessUsageDescription: 'Giles manages calendar events when you request it.',
      NSRemindersFullAccessUsageDescription: 'Giles manages reminders when you request it.'
    }
  },
  dmg: {
    shrink: false,
    title: 'Giles Installer',
    icon: 'assets/icon.icns',
    backgroundColor: '#142832',
    iconSize: 96,
    iconTextSize: 11,
    window: { width: 660, height: 400 },
    contents: [{ x: 180, y: 200, type: 'file' }, { x: 480, y: 200, type: 'link', path: '/Applications' }]
  }
}
