import os from 'node:os'
import path from 'node:path'

if (process.platform !== 'darwin' || process.arch !== 'arm64') {
  throw new Error('Giles supports macOS Apple Silicon only.')
}
// Bind before main or Python resolves paths; inherited Hermes variables must
// never redirect this personal app into the original application's data.
process.env.HERMES_HOME = process.env.GILES_HOME || path.join(os.homedir(), '.giles')
process.env.HERMES_RUNTIME_DIR = path.join(process.env.HERMES_HOME, 'tools')

await import('./main')
