"""Build Giles with the unchanged upstream native Python payload machinery."""
from __future__ import annotations
import json
import os
import platform
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

def main() -> None:
    if sys.platform != 'darwin' or platform.machine() != 'arm64':
        raise SystemExit('Giles requires a native macOS Apple Silicon builder.')
    product = json.loads((ROOT / 'giles.json').read_text(encoding='utf-8-sig'))
    if not os.environ.get('GILES_SIGNING_KEYCHAIN'):
        raise SystemExit('A Giles signing keychain is required.')
    from scripts.bundles.desktop import build_prepared
    from scripts.bundles.desktop_prepare import BuildRequest, prepare
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, timeout=120, encoding='utf-8').strip()
    request = BuildRequest.create(ROOT, tag=None, commit=commit, variant='bundled', work=ROOT / '.build/desktop-job', cache=ROOT / '.cache/desktop-inputs', bundle_env={})
    request = replace(request, version=product['version'])
    build_prepared(prepare(request), ['--arm64', '--publish', 'never'])
if __name__ == '__main__':
    main()
