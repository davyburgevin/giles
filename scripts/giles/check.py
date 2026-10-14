"""Validate Giles product inputs without installing the agent engine."""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
product = json.loads((ROOT / 'giles.json').read_text(encoding='utf-8-sig'))
assert re.fullmatch('\\d+\\.\\d+\\.\\d+', product['version']), 'Invalid Giles release version'
assert product['repository'] == 'davyburgevin/giles'
assert product['appId'] == 'fr.davyburgevin.giles'
assert product['platform'] == 'darwin' and product['arch'] == 'arm64'
assert json.loads((ROOT / 'apps/desktop/package.json').read_text(encoding='utf-8-sig'))['version'] == product['version']
print('Giles product inputs verified.')
