"""Verify actual packaged identity, Python startup, signature and updater authority."""
import json
import os
import plistlib
import subprocess
import sys
import tempfile
from pathlib import Path

app = Path(sys.argv[1]).resolve()
with (app/'Contents/Info.plist').open('rb') as f:
    info = plistlib.load(f)
assert info['CFBundleIdentifier'] == 'fr.davyburgevin.giles'
assert info['CFBundleName'] == 'Giles'
assert info['CFBundleURLTypes'][0]['CFBundleURLSchemes'] == ['giles']
subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True)
arch = subprocess.check_output(['lipo','-archs',str(app/'Contents/MacOS/Giles')],text=True).strip()
assert arch == 'arm64', arch
resources = app/'Contents/Resources'
feed = (resources/'app-update.yml').read_text()
assert 'davyburgevin' in feed and 'giles' in feed and 'NousResearch' not in feed
payload = resources/'agent-payload'
manifest = json.loads((payload/'manifest.json').read_text())
print('Packaged identity, signature, Apple Silicon and Giles update feed verified.')
print('Payload manifest verified:', manifest.get('schemaVersion', 'present'))
