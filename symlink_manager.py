"""
Cross-platform symlink management module.
Handles symlink creation for Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Tuple, Optional, List


class SymlinkManager:
    """Manages symlink creation across different platforms."""
    
    # Class-level cache: tracks whether we've already detected admin elevation
    _is_elevated = None
    
    @staticmethod
    def is_windows():
        """Check if running on Windows."""
        return platform.system() == "Windows"
    
    @staticmethod
    def is_macos():
        """Check if running on macOS."""
        return platform.system() == "Darwin"
    
    @staticmethod
    def is_linux():
        """Check if running on Linux."""
        return platform.system() == "Linux"
    
    @staticmethod
    def _check_elevated() -> bool:
        """Check if the current process is running with admin privileges."""
        if SymlinkManager._is_elevated is not None:
            return SymlinkManager._is_elevated
        try:
            if SymlinkManager.is_windows():
                import ctypes
                SymlinkManager._is_elevated = ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                SymlinkManager._is_elevated = os.geteuid() == 0
        except Exception:
            SymlinkManager._is_elevated = False
        return SymlinkManager._is_elevated

    @staticmethod
    def _safe_remove_target(target_path: Path) -> Tuple[bool, str]:
        """
        Safely remove a target path — ONLY if it is a symlink.
        Refuses to delete real files or directories to prevent accidental
        data loss (e.g. rmdir on an important system folder).

        Args:
            target_path: The Path to remove.

        Returns:
            (success, message) tuple.
        """
        if not target_path.exists() and not target_path.is_symlink():
            return True, "Target does not exist — nothing to remove."

        if not target_path.is_symlink():
            return False, (
                f"Refusing to remove '{target_path}' — it is a real "
                f"{'directory' if target_path.is_dir() else 'file'}, not a symlink. "
                "Only symlinks can be force-removed."
            )

        try:
            target_path.unlink()
            return True, f"Removed existing symlink: {target_path}"
        except Exception as e:
            return False, f"Failed to remove symlink '{target_path}': {e}"

    @staticmethod
    def run_mklink_batch(operations: List[Tuple[str, str, bool, bool]]) -> Tuple[bool, str]:
        """
        Windows only: build a temporary .bat file with mklink commands and
        run it elevated via ShellExecuteW (runas).  This avoids needing to
        run the entire app as admin.

        Each operation is: (source, target, is_dir, force)

        Returns (success, message) where message is a summary or error.
        """
        if not SymlinkManager.is_windows():
            return False, "Not supported on this platform"

        lines = ["@echo off", "chcp 65001 >nul", "setlocal enabledelayedexpansion", ""]
        for i, (source, target, is_dir, force) in enumerate(operations):
            # Normalise to Windows backslashes — mklink does not accept /
            src = source.replace('/', '\\')
            tgt = target.replace('/', '\\')
            target_path = Path(target)
            if force and target_path.exists():
                if target_path.is_symlink():
                    if target_path.is_dir():
                        lines.append(f'rmdir "{tgt}" 2>nul')
                    else:
                        lines.append(f'del "{tgt}" 2>nul')
                else:
                    # Safety: refuse to remove real files/directories in batch mode
                    lines.append(f'echo SKIP,{i} — "{tgt}" is a real file/dir, not a symlink')
            lines.append(f'echo OP,{i},src="{src}",tgt="{tgt}"')
            if is_dir:
                lines.append(f'mklink /D "{tgt}" "{src}"')
            else:
                lines.append(f'mklink "{tgt}" "{src}"')
            lines.append(f'if errorlevel 1 (echo FAIL,{i}) else (echo OK,{i})')
            lines.append("")

        lines.append("endlocal")
        batch_content = "\r\n".join(lines)

        import tempfile
        import time
        batch_path = Path(tempfile.gettempdir()) / f"symlink_mklink_{int(time.time())}.bat"
        log_path = batch_path.with_suffix(".log")

        try:
            batch_path.write_text(batch_content, encoding="utf-8-sig")

            # Write a wrapper that redirects all output to a log file, then deletes itself
            wrapper_path = batch_path.with_suffix(".wrapper.bat")
            wrapper = f"""@echo off
cd /d "%~dp0"
call "{batch_path}" > "{log_path}" 2>&1
"""
            wrapper_path.write_text(wrapper, encoding="utf-8-sig")

            # Elevate via ShellExecuteW with "runas" verb.
            # Run cmd.exe /c with the wrapper path so elevation is inherited.
            import ctypes
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe",
                f'/c "{wrapper_path}"',
                str(batch_path.parent), 0  # SW_HIDE
            )
            if result <= 32:
                return False, f"UAC prompt was cancelled or failed (code={result})"

            # Wait for the log file to appear and stabilise
            waited = 0
            while waited < 60:
                if log_path.exists():
                    time.sleep(0.5)
                    break
                time.sleep(0.5)
                waited += 1

            # Wait for the process to finish — poll until log stops growing
            prev_size = -1
            stable_count = 0
            while stable_count < 3 and waited < 120:
                if log_path.exists():
                    cur_size = log_path.stat().st_size
                    if cur_size == prev_size:
                        stable_count += 1
                    else:
                        stable_count = 0
                    prev_size = cur_size
                time.sleep(0.5)
                waited += 1

            # Parse results
            failures = 0
            skips = 0
            total = len(operations)
            if log_path.exists():
                log_text = log_path.read_text(encoding="utf-8", errors="replace")
                for l in log_text.splitlines():
                    if l.startswith("SKIP,"):
                        skips += 1
                        logging.warning(l)
                    elif l.startswith("FAIL,"):
                        logging.warning(l)
                    else:
                        logging.info(l)
                for line in log_text.splitlines():
                    if line.startswith("FAIL,"):
                        failures += 1
                    elif line.startswith("SKIP,"):
                        failures += 1

            # Cleanup
            for p in [batch_path, wrapper_path, log_path]:
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass

            if failures:
                return False, f"{failures}/{total} symlink(s) failed — check permissions or paths"
            return True, f"All {total} symlink(s) created successfully via elevated batch"

        except Exception as e:
            return False, f"Elevated batch failed: {e}"

    @staticmethod
    def run_batch(operations: List[Tuple[str, str, bool, bool, bool, bool]]) -> Tuple[bool, str, List[Tuple[str, str, bool, str]]]:
        """
        Cross-platform batch symlink creation.

        Each operation tuple is: (source, target, is_dir, force, relative, admin)

        On Windows with admin=True and not already elevated, delegates to
        run_mklink_batch().  On all other platforms runs each operation
        directly via os.symlink() / mklink.

        Returns (overall_success, summary_message, per_result_details).
        """
        results: List[Tuple[str, str, bool, str]] = []

        # --- Windows elevated batch path ---
        if SymlinkManager.is_windows() and operations:
            needs_admin = any(op[5] for op in operations) if len(operations[0]) > 5 else False
            if needs_admin and not SymlinkManager._check_elevated():
                mklink_ops = [(s, t, d, f) for s, t, d, f, _, _ in operations]
                success, msg = SymlinkManager.run_mklink_batch(mklink_ops)
                for s, t, _, _, _, _ in operations:
                    results.append((s, t, success, msg))
                return success, msg, results

        # --- Direct path (all platforms) ---
        failures = 0
        for source, target, is_dir, force, relative, _admin in operations:
            try:
                target_path = Path(target)

                if force and (target_path.exists() or target_path.is_symlink()):
                    ok, msg = SymlinkManager._safe_remove_target(target_path)
                    if not ok:
                        results.append((source, target, False, msg))
                        failures += 1
                        continue

                if SymlinkManager.is_windows():
                    # Use the battle-tested create_symlink logic which handles
                    # os.symlink fallback, mklink, and ADMIN_REQUIRED detection
                    success, msg = SymlinkManager.create_symlink(
                        source, target, relative, force, _admin
                    )
                    if success:
                        results.append((source, target, True, msg))
                    else:
                        results.append((source, target, False, msg))
                        if msg == "ADMIN_REQUIRED":
                            failures += 1
                else:
                    # macOS / Linux
                    src = source
                    if relative:
                        try:
                            src = os.path.relpath(source, target_path.parent)
                        except ValueError:
                            pass
                    os.symlink(src, target)
                    results.append((source, target, True, "Created"))
            except FileExistsError:
                results.append((source, target, False, "Target already exists"))
                failures += 1
            except Exception as e:
                results.append((source, target, False, str(e)))
                failures += 1

        total = len(operations)
        if failures:
            return False, f"{failures}/{total} symlink(s) failed", results
        return True, f"All {total} symlink(s) created successfully", results

    @staticmethod
    def validate_paths(source: str, target: str) -> Tuple[bool, str]:
        """
        Validate source and target paths.
        
        Args:
            source: Source path to link to
            target: Target symlink path
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not source or not target:
            return False, "Both source and target paths must be specified."
        
        source_path = Path(source)
        target_path = Path(target)
        
        # Check if source exists
        if not source_path.exists():
            return False, f"Source path does not exist: {source}"
        
        # Check if target already exists
        if target_path.exists() or target_path.is_symlink():
            return False, f"Target path already exists: {target}"
        
        # Check if target parent directory exists
        if not target_path.parent.exists():
            return False, f"Target parent directory does not exist: {target_path.parent}"
        
        # Check write permissions for target directory
        if not os.access(target_path.parent, os.W_OK):
            return False, f"No write permission for target directory: {target_path.parent}"
        
        return True, ""
    
    @staticmethod
    def create_symlink(
        source: str,
        target: str,
        relative: bool = False,
        force: bool = False,
        admin: bool = False
    ) -> Tuple[bool, str]:
        """
        Create a symlink.
        
        Args:
            source: Source path to link to
            target: Target symlink path
            relative: Create relative symlink (if supported)
            force: Force creation even if target exists
            admin: Use admin/sudo privileges (for Windows/Linux)
            
        Returns:
            Tuple of (success, message)
        """
        # Validate paths
        valid, error = SymlinkManager.validate_paths(source, target)
        if not valid and not force:
            return False, error
        
        source_path = Path(source).resolve()
        target_path = Path(target)
        
        if SymlinkManager.is_windows():
            return SymlinkManager._create_symlink_windows(
                str(source_path), str(target_path), relative, force, admin
            )
        elif SymlinkManager.is_macos() or SymlinkManager.is_linux():
            return SymlinkManager._create_symlink_unix(
                str(source_path), str(target_path), relative, force
            )
        else:
            return False, "Unsupported operating system."
    
    @staticmethod
    def _create_symlink_windows(
        source: str,
        target: str,
        relative: bool = False,
        force: bool = False,
        admin: bool = False
    ) -> Tuple[bool, str]:
        """Create symlink on Windows."""
        try:
            source_path = Path(source)
            target_path = Path(target)
            is_dir = source_path.is_dir()

            # Remove existing target if force is set
            if force and target_path.exists():
                ok, msg = SymlinkManager._safe_remove_target(target_path)
                if not ok:
                    return False, msg

            # If admin mode was requested and we're not already elevated,
            # skip straight to the .bat elevation approach
            if admin and not SymlinkManager._check_elevated():
                ops = [(source, target, is_dir, force)]
                return SymlinkManager.run_mklink_batch(ops)

            # If already elevated, skip directly to mklink
            if SymlinkManager._check_elevated():
                cmd = "mklink"
                if is_dir:
                    cmd += " /D"
                cmd += f' "{target_path}" "{source_path}"'
                # mklink is a cmd.exe internal command — must use shell=True
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    check=False, shell=True
                )
                if result.returncode == 0:
                    return True, f"Symlink created successfully: {target}"
                return False, f"Failed to create symlink: {result.stderr}"

            # Try Python's os.symlink() — works on Win10+ with Developer Mode
            try:
                os.symlink(source, target, target_is_directory=is_dir)
                return True, f"Symlink created successfully: {target}"
            except OSError:
                pass

            # Try mklink directly (may work without admin on some systems)
            try:
                cmd = "mklink"
                if is_dir:
                    cmd += " /D"
                cmd += f' "{target_path}" "{source_path}"'
                # mklink is a cmd.exe internal command — must use shell=True
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    check=False, shell=True
                )
                if result.returncode == 0:
                    return True, f"Symlink created successfully: {target}"
            except Exception:
                pass

            # Not elevated and admin mode was requested — use .bat elevation
            if admin:
                ops = [(source, target, is_dir, force)]
                return SymlinkManager.run_mklink_batch(ops)

            # Not elevated and all non-admin methods failed.
            return False, "ADMIN_REQUIRED"

        except Exception as e:
            return False, f"Error creating symlink on Windows: {e}"
    
    @staticmethod
    def _create_symlink_unix(
        source: str,
        target: str,
        relative: bool = False,
        force: bool = False
    ) -> Tuple[bool, str]:
        """Create symlink on Unix-like systems (macOS and Linux)."""
        try:
            source_path = Path(source)
            target_path = Path(target)
            
            # Handle relative symlinks
            if relative:
                try:
                    source_rel = os.path.relpath(source, target_path.parent)
                    source = source_rel
                except ValueError:
                    # On different drives/filesystems, relative might not work
                    pass
            
            # Remove target if force is set and it exists
            if force and (target_path.exists() or target_path.is_symlink()):
                ok, msg = SymlinkManager._safe_remove_target(target_path)
                if not ok:
                    return False, msg
            
            # Create the symlink
            try:
                os.symlink(source, target)
                symlink_type = "relative" if relative else "absolute"
                return True, f"Symlink created successfully ({symlink_type}): {target}"
            except FileExistsError:
                return False, f"Target already exists: {target}"
            except Exception as e:
                return False, f"Error creating symlink: {e}"
        
        except Exception as e:
            return False, f"Error creating symlink on Unix: {e}"
    
    @staticmethod
    def remove_symlink(target: str) -> Tuple[bool, str]:
        """
        Remove a symlink.
        
        Args:
            target: Symlink path to remove
            
        Returns:
            Tuple of (success, message)
        """
        try:
            target_path = Path(target)
            
            if not target_path.is_symlink():
                return False, f"Target is not a symlink: {target}"
            
            target_path.unlink()
            return True, f"Symlink removed successfully: {target}"
        except Exception as e:
            return False, f"Error removing symlink: {e}"
    
    @staticmethod
    def get_symlink_info(target: str) -> Optional[dict]:
        """
        Get information about a symlink.
        
        Args:
            target: Symlink path
            
        Returns:
            Dictionary with symlink info or None if not a symlink
        """
        try:
            target_path = Path(target)
            
            if not target_path.is_symlink():
                return None
            
            return {
                "path": str(target_path),
                "target": str(target_path.readlink()),
                "exists": target_path.exists(),
                "is_dir": target_path.is_dir(),
                "size": target_path.lstat().st_size if target_path.is_symlink() else None,
            }
        except Exception as e:
            return None

    @staticmethod
    def merge_directories(source: str, target_symlink: str) -> Tuple[bool, str, list]:
        """
        Two-way merge between the symlink's parent directory and the source directory.

        For each item (file or folder) that exists in the symlink's parent directory
        but does NOT exist in the source directory:
          1. Copy the item into the source directory
          2. Delete the item from the symlink's parent directory
          3. Create a new symlink in the symlink's parent directory pointing to the
             corresponding item in the source directory

        Items that already exist in the source are left untouched (they are already
        accessible through the main symlink). Duplicate items (same resolved path)
        are silently skipped.

        Args:
            source: The original source directory that the symlink points to.
            target_symlink: The path of the symlink itself (its parent is scanned).

        Returns:
            (success, message, new_symlinks) where new_symlinks is a list of
            dicts with 'source' and 'target' keys for each newly created symlink.
        """
        source_path = Path(source)
        symlink_path = Path(target_symlink)
        scan_root = symlink_path.parent  # The directory containing the symlink

        if not source_path.is_dir():
            return False, f"Source is not a directory: {source}", []

        if not scan_root.is_dir():
            return False, f"Symlink parent directory does not exist: {scan_root}", []

        logging.info(f"Merge: scanning '{scan_root}' for items not in source '{source}'")

        merged = 0
        skipped = 0
        errors = 0
        new_symlinks = []
        seen_paths = set()  # Track resolved paths to silently ignore duplicates

        try:
            # Walk every item in the symlink's parent directory
            for item in list(scan_root.iterdir()):
                item_name = item.name

                # Silently ignore duplicate resolved paths
                try:
                    resolved = item.resolve()
                    if str(resolved) in seen_paths:
                        continue
                    seen_paths.add(str(resolved))
                except Exception:
                    pass

                # Skip the symlink itself
                if item.resolve() == symlink_path.resolve() or item.name == symlink_path.name:
                    skipped += 1
                    continue

                # Skip items whose name matches the source directory name — that data
                # belongs to the main symlink path and will be handled by its recreation.
                if item_name == source_path.name:
                    skipped += 1
                    continue

                # Skip items that are already symlinks pointing into the source
                try:
                    if item.is_symlink():
                        resolved = item.resolve()
                        if str(resolved).startswith(str(source_path.resolve())):
                            skipped += 1
                            continue
                except Exception:
                    pass

                dest_in_source = source_path / item_name

                # Check if this item already exists in the source
                if dest_in_source.exists():
                    # Compare timestamps: if the incoming item is newer,
                    # overwrite the existing source copy
                    try:
                        src_mtime = dest_in_source.stat().st_mtime
                        item_mtime = item.stat().st_mtime if not item.is_symlink() else 0
                        if item_mtime <= src_mtime:
                            skipped += 1
                            continue
                        # Incoming is newer — proceed to overwrite below
                    except Exception:
                        skipped += 1
                        continue

                # --- This item exists in the symlink dir but NOT in source,
                #     or is newer than the source copy ---
                try:
                    if item.is_dir():
                        # Copy the entire directory tree to source
                        shutil.copytree(str(item), str(dest_in_source), dirs_exist_ok=True)
                        # Remove the original from the symlink directory
                        shutil.rmtree(str(item))
                    else:
                        # Copy the file to source
                        shutil.copy2(str(item), str(dest_in_source))
                        # Remove the original from the symlink directory
                        item.unlink()

                    # Record the symlink to be created (batch will handle it)
                    new_target = str(scan_root / item_name)
                    new_source = str(dest_in_source)
                    dest_in_source_path = Path(dest_in_source)
                    new_symlinks.append({
                        'source': new_source,
                        'target': new_target,
                        'is_dir': dest_in_source_path.is_dir(),
                    })
                    merged += 1
                    logging.info(f"Merge: moved '{item_name}' to source — queued for batch symlink creation")

                except Exception as e:
                    errors += 1
                    logging.error(f"Merge: error processing '{item_name}': {e}")

            logging.info(
                f"Merge complete: {merged} item(s) merged, {skipped} skipped, "
                f"{errors} error(s)"
            )
            summary = f"Merged {merged} item(s), {skipped} skipped, {errors} errors"
            return True, summary, new_symlinks

        except Exception as e:
            logging.error(f"Merge failed for '{source}' -> '{scan_root}': {e}")
            return False, f"Merge failed: {e}", []
