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
- **Merge refactored** — Replaced per-symlink merge checkbox with a **Merge Settings** dialog: users define source → target directory pairs; merge runs on every persistence tick, scanning target folders for files not in source
- **Timestamp-aware overwrites** — Merge only overwrites source files when the incoming file has a newer modification time; older files are silently skipped
- **Overwrite confirmation** — Before the merge phase runs, a batch-aware dialog lists all pending overwrites and asks for the user's approval
- **Persistence improved** — Admin retry flag prevents multiple UAC prompts stacking up; retry only fires once until the batch completes
- **Merge runs every persistence check** — No longer tied to missing symlinks; merge scans target directories every tick, catching files added by external processes
- **Cross-platform audit** — Removed unused imports, verified all platform-specific code is properly guarded

### Fixed
- Triple UAC prompt issue
- Missing symlink prompt now shows once per session with a persistence-aware tip
- Duplicate batch operations from merge sub-symlinks