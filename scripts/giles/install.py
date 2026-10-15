"""Install the verified Giles release from a Git checkout, without compiling."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import plistlib
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

REPOSITORY = 'davyburgevin/giles'
IDENTIFIER = 'fr.davyburgevin.giles'
SIGNER = 'c685007d658457012d8332b0edee6eeb9755ce6a'
REQUIREMENT = f'identifier "{IDENTIFIER}" and anchor = H"{SIGNER}"'


def release_asset() -> tuple[dict, dict]:
    request = Request(
        f'https://api.github.com/repos/{REPOSITORY}/releases/latest',
        headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'Giles-installer'},
    )
    with urlopen(request, timeout=60) as response:
        release = json.load(response)
    version = release['tag_name'].removeprefix('giles-v')
    filename = f'Giles-{version}-mac-arm64.zip'
    asset = next(item for item in release['assets'] if item['name'] == filename)
    expected_url = f'https://github.com/{REPOSITORY}/releases/download/{release["tag_name"]}/{filename}'
    if asset['browser_download_url'] != expected_url:
        raise RuntimeError('Unexpected Giles release download URL.')
    if not asset.get('digest', '').startswith('sha256:'):
        raise RuntimeError('The release does not provide a SHA-256 digest.')
    return release, asset


def verify_archive(archive: Path, asset: dict) -> None:
    digest = hashlib.sha256()
    with archive.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    if f'sha256:{digest.hexdigest()}' != asset['digest']:
        raise RuntimeError('The archive does not match the published Giles SHA-256 digest.')


def verify_app(app: Path, version: str) -> None:
    with (app / 'Contents/Info.plist').open('rb') as source:
        info = plistlib.load(source)
    if info.get('CFBundleIdentifier') != IDENTIFIER or info.get('CFBundleShortVersionString') != version:
        raise RuntimeError('Unexpected Giles application identity or version.')
    subprocess.run(
        ['/usr/bin/codesign', '--verify', '--deep', '--strict', '-R', REQUIREMENT, str(app)],
        check=True, timeout=180,
    )
    architecture = subprocess.check_output(
        ['/usr/bin/lipo', '-archs', str(app / 'Contents/MacOS/Giles')],
        text=True, encoding='utf-8', timeout=30,
    ).strip()
    if architecture != 'arm64':
        raise RuntimeError('Giles requires the Apple Silicon application.')


def install_app(app: Path, destination: Path) -> None:
    backup = destination.with_name('Giles.previous.app')
    if backup.exists() or backup.is_symlink():
        raise RuntimeError(f'Previous installation backup already exists: {backup}')
    had_previous = destination.exists()
    if had_previous:
        # Refuse to overwrite another application placed at the same location.
        with (destination / 'Contents/Info.plist').open('rb') as source:
            if plistlib.load(source).get('CFBundleIdentifier') != IDENTIFIER:
                raise RuntimeError('The destination contains an application other than Giles.')
        destination.rename(backup)
    try:
        app.rename(destination)
    except OSError:
        if had_previous:
            backup.rename(destination)
        raise
    if had_previous:
        shutil.rmtree(backup)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='Reuse a downloaded release ZIP; its digest is still verified.')
    parser.add_argument('--applications-dir', type=Path, default=Path.home() / 'Applications')
    parser.add_argument('--bin-dir', type=Path, default=Path.home() / '.local/bin')
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('Giles requires macOS on Apple Silicon.')
    running = subprocess.run(['/usr/bin/pgrep', '-x', 'Giles'], capture_output=True, timeout=30, check=False)
    if running.returncode == 0:
        raise SystemExit('Quit Giles before installing or replacing it.')
    release, asset = release_asset()
    version = release['tag_name'].removeprefix('giles-v')
    applications = args.applications_dir.expanduser().resolve()
    binary_dir = args.bin_dir.expanduser().resolve()
    destination = applications / 'Giles.app'
    launcher = binary_dir / 'giles'
    if launcher.exists() and 'Giles desktop launcher' not in launcher.read_text(encoding='utf-8'):
        raise SystemExit(f'Refusing to replace an existing command: {launcher}')
    applications.mkdir(parents=True, exist_ok=True)
    binary_dir.mkdir(parents=True, exist_ok=True)
    # Staging on the destination volume makes the final rename atomic.
    with tempfile.TemporaryDirectory(prefix='.giles-install-', dir=applications) as folder:
        staging = Path(folder)
        archive = args.archive.expanduser().resolve() if args.archive else staging / asset['name']
        if not args.archive:
            print(f'Downloading Giles {version} ({asset["size"] // 1_000_000} MB)…', flush=True)
            with urlopen(asset['browser_download_url'], timeout=120) as source, archive.open('wb') as output:
                shutil.copyfileobj(source, output)
        print('Verifying the release archive…', flush=True)
        verify_archive(archive, asset)
        subprocess.run(['/usr/bin/ditto', '-x', '-k', str(archive), str(staging)], check=True, timeout=600)
        app = staging / 'Giles.app'
        verify_app(app, version)
        install_app(app, destination)
    command = f'#!/bin/sh\n# Giles desktop launcher\nexec /usr/bin/open {shlex.quote(str(destination))} --args "$@"\n'
    with tempfile.NamedTemporaryFile(mode='w', dir=binary_dir, encoding='utf-8', delete=False) as output:
        output.write(command)
        temporary_launcher = Path(output.name)
    temporary_launcher.chmod(0o755)
    os.replace(temporary_launcher, launcher)
    print(f'Giles {version} installed: {destination}\nLaunch with: {launcher}')
    if str(binary_dir) not in os.environ.get('PATH', '').split(os.pathsep):
        print(f'Add this directory to your shell PATH: {binary_dir}')


if __name__ == '__main__':
    main()
