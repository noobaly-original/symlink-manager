# Changelog

All notable changes to this project will be documented in this file.

---

## [2.1.0] — 2026-07-13

### Added
- **Symlink Persistence** — New optional feature in Settings that automatically checks all tracked symlinks every 60 seconds and recreates any that are missing. Cross-platform (Windows, macOS, Linux).
  - Settings checkbox: "Persist symlinks — automatically recreate missing symlinks"
  - Immediate check runs when the option is enabled
  - **Batch-aware**: all missing symlinks are recreated in a single batch operation
  - **Admin notification**: if admin privileges are needed, user is notified and retry happens 15 seconds later with elevated rights
  - Status bar notification when symlinks are restored
  - Full logging at debug/info/warning/error levels
  - Timer starts automatically if persistence was enabled in a previous session
- **Merge Management** — New optional feature that scans the symlink's parent directory for items not in the source, copies them to source, removes from target, and creates per-item symlinks. Works alongside persistence.
  - Settings checkbox: "Merge management — merge source into symlink folder before recreating"
  - **Batch-aware**: newly created sub-symlinks are created as part of the main batch operation
  - **Per-source control**: merge checkbox in the Manage tab applies to a source directory (affects all symlinks sharing that source)
  - **Duplicate detection**: items pointing to the same resolved path are silently skipped
  - New sub-symlinks are automatically tracked in the Manage tab
  - Full logging of merge operations
  - Cross-platform: works on Windows, macOS, and Linux

### Changed
- Updated version to v2.1.0

---

## [2.0.2] — Initial release