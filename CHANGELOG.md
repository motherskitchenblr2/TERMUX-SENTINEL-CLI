# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 - 2026-11-07

### Added

- Core `Termux_Sentinel.py` system cleaner and process supervisor.
- Cyber Slant ASCII header with Terminal Width auto-lock ($\le 44$ columns)
  and neon gradient palette.
- Interactive TUI and command-line interface (`sentinel ui`, `sentinel audit`,
  `sentinel clean`, `sentinel vault`, `sentinel apps`, `sentinel bots`,
  `sentinel cloud`).
- Safety Vault subsystem (`vault.json`) protecting WhatsApp media, root
  storage, and user development garages.
- Dual-direction cloud migration and live backup workflows via Rclone
  (`Backup_to_Drive.sh`, `migrate_to_cmf_bkp.sh`, `migrate_to_realme_bkp.sh`).
- Project packaging configuration (`pyproject.toml`, `requirements.txt`,
  `requirements-dev.txt`).
- Automated CI pipeline with 8 GitHub Action workflows (Lint, Bug Detection,
  Dependencies, Security, PR Review, Merge Conflict, Refactor, Codacy Analysis).
- Unit test suite (`tests/test_smoke.py`).
- Security policy (`SECURITY.md`) and contribution guidelines
  (`CONTRIBUTING.md`).

### Changed

- Unified codebase into root directory, archiving legacy mirror files into
  `docs/archive/`.
- Hardened CI workflows with pytest error code guards and Dependabot
  automation.
