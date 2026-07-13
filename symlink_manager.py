"""
Cross-platform symlink management module.
Handles symlink creation for Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
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
                if target_path.is_dir() and not target_path.is_symlink():
                    lines.append(f'rmdir "{tgt}" 2>nul')
                else:
                    lines.append(f'del "{tgt}" 2>nul')
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
            total = len(operations)
            if log_path.exists():
                log_text = log_path.read_text(encoding="utf-8", errors="replace")
                for l in log_text.splitlines():
                    if not l.startswith("if errorlevel") and not l.startswith("FAIL"):
                        logging.info(l)
                    else:
                        logging.warning(l)
                for line in log_text.splitlines():
                    if line.startswith("FAIL,"):
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
                    if target_path.is_dir() and not target_path.is_symlink():
                        os.rmdir(str(target_path))
                    else:
                        target_path.unlink()

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
                try:
                    if target_path.is_dir() and not target_path.is_symlink():
                        os.rmdir(str(target_path))
                    else:
                        target_path.unlink()
                except Exception as e:
                    return False, f"Could not remove existing target: {e}"

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
                try:
                    if target_path.is_symlink():
                        target_path.unlink()
                    elif target_path.is_dir():
                        os.rmdir(target)
                    else:
                        target_path.unlink()
                except Exception as e:
                    return False, f"Could not remove existing target: {e}"
            
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
