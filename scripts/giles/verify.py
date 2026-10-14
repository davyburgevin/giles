"""Verify actual packaged identity, Python startup, signature and updater authority."""
import json
import os
import plistlib
import subprocess
import sys
import tempfile
from pathlib import Path
app = Path(sys.argv[1]).resolve()
with (app / 'Contents/Info.plist').open('rb') as f:
    info = plistlib.load(f)
assert info['CFBundleIdentifier'] == 'fr.davyburgevin.giles'
assert info['CFBundleName'] == 'Giles'
assert info['CFBundleURLTypes'][0]['CFBundleURLSchemes'] == ['giles']
subprocess.run(['codesign', '--verify', '--deep', '--strict', str(app)], check=True, timeout=120)
arch = subprocess.check_output(['lipo', '-archs', str(app / 'Contents/MacOS/Giles')], text=True, timeout=120, encoding='utf-8').strip()
assert arch == 'arm64', arch
resources = app / 'Contents/Resources'
feed = (resources / 'app-update.yml').read_text(encoding='utf-8-sig')
assert 'davyburgevin' in feed and 'giles' in feed and ('NousResearch' not in feed)
payload = resources / 'agent-payload'
manifest = json.loads((payload / 'manifest.json').read_text(encoding='utf-8-sig'))
print('Packaged identity, signature, Apple Silicon and Giles update feed verified.')
assert manifest['target'] == 'darwin-arm64'
runtime = manifest['runtime']
launcher = payload / runtime['commands']['hermes']
assert launcher.name == 'giles'
with tempfile.TemporaryDirectory(prefix='giles-smoke-') as folder:
    environment = dict(os.environ, HERMES_HOME=folder, HERMES_RUNTIME_DIR=str(Path(folder) / 'tools'), HERMES_DESKTOP='1', HERMES_SERVE_HEADLESS='1')
    result = subprocess.run([str(launcher), '--help'], env=environment, capture_output=True, text=True, timeout=60, check=False, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    assert 'serve' in result.stdout
    log = Path(folder) / 'backend.log'
    with log.open('w', encoding='utf-8') as output:
        process = subprocess.Popen([str(launcher), 'serve', '--port', '0'], env=environment, stdout=output, stderr=output)
        try:
            import re
            import time
            deadline = time.monotonic() + 60
            match = None
            while time.monotonic() < deadline and process.poll() is None:
                match = re.search(r'HERMES_BACKEND_READY port=(\d+)', log.read_text(encoding='utf-8-sig'))
                if match:
                    break
                time.sleep(0.25)
            if not match:
                raise RuntimeError(log.read_text(encoding='utf-8-sig'))
            print('Original Python backend started successfully on an isolated ephemeral port.')
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
print('Packaged Python launcher and native backend startup verified.')
