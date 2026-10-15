# Giles

Personal AI assistant for **macOS Apple Silicon only**, forked from [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent).

Giles preserves the original Python engine and Electron interface. Python module names and internal `HERMES_*` contracts remain compatible to keep upstream merges manageable. Application identity is independent: `fr.davyburgevin.giles`, `Giles.app`, `giles://`, CLI `giles`, agent state `~/.giles`, desktop state `~/Library/Application Support/Giles`.

## Install from Git

```sh
git clone https://github.com/davyburgevin/giles.git
cd giles
./install.sh
giles
```

The installer requires Git and Python 3 on macOS Apple Silicon. It downloads the latest compiled Giles release, verifies its published SHA-256, application identity and personal signing certificate, and installs it into `~/Applications/Giles.app`. It creates the `giles` launcher in `~/.local/bin`; add that directory to your shell PATH if requested. No local compilation, signing key or Homebrew installation is needed.

For later updates, use **Giles → Check for Updates…**. You can also quit Giles and rerun `./install.sh` to install the latest published release. Conversations and settings live outside the application and are preserved. Pulling Git changes alone does not update the installed application.

## Distribution

[Giles releases](https://github.com/davyburgevin/giles/releases) contain an ARM64 DMG and ZIP with Python, dependencies and managed tools embedded. The app checks this repository's releases for updates. A persistent personal self-signed certificate signs local and CI builds; releases are not notarized by Apple. Keep `.giles-signing/` backed up privately: changing the certificate can prevent existing installations accepting updates. Private signing material is ignored and stored in GitHub Actions secrets, never committed.

`giles.json` and `apps/desktop/package.json` own the Giles version, independently of the upstream Python package. The **Giles · Apple Silicon build and release** workflow builds on demand; its release option publishes after verification. Tags `giles-vX.Y.Z` also trigger publication. Release assets include `latest-mac.yml` for the application's updater.

## Upstream synchronization

**Giles · Sync upstream on demand** fetches `NousResearch/hermes-agent` and opens a PR into Giles `main`. It never merges automatically. Conflicting integrations open a draft recording affected paths, for resolution before the actual engine update. Original upstream workflows are archived under `.github/upstream-workflows/`; only Giles workflows run in this fork.

## Local build

`scripts/giles/build.py` reuses the upstream native bundle preparer and requires a clean committed checkout, native macOS ARM64 and the Giles signing keychain. `scripts/giles/signing.py` manages the dedicated signing keychain. Build outputs live in `apps/desktop/release/`.

## License and attribution

The original engine is Copyright Nous Research under the MIT license. The original [LICENSE](LICENSE) and notices are retained. Giles is a personal derivative, independently maintained by Davy Burgevin, without affiliation with Nous Research.
