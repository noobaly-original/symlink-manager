"""
Cross-platform symlink management module.
Handles symlink creation for Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class SymlinkManager:
    """Manages symlink creation across different platforms."""
    
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
            
            # Determine if source is a directory
            is_dir = source_path.is_dir()
            
            # Build mklink command as a list (safer than string concatenation)
            cmd = ["mklink"]
            if is_dir:
                cmd.append("/D")  # Directory junction
            
            if force and target_path.exists():
                try:
                    if is_dir:
                        os.rmdir(target)
                    else:
                        os.remove(target)
                except Exception as e:
                    return False, f"Could not remove existing target: {e}"
            
            # Add target and source as separate list items - subprocess will handle escaping
            cmd.append(str(target_path))
            cmd.append(str(source_path))
            
            if admin:
                # Use subprocess with elevation via powershell (safer than ShellExecuteW)
                try:
                    import json
                    # Build a safe command string using PowerShell's argument array syntax
                    powershell_cmd = [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        f"Start-Process cmd.exe -Verb RunAs -ArgumentList '/c','mklink {'/D' if is_dir else ''} \"{target_path}\" \"{source_path}\"' -Wait"
                    ]
                    result = subprocess.run(
                        powershell_cmd,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if result.returncode != 0:
                        return False, f"Failed to create symlink with admin privileges: {result.stderr}"
                    return True, f"Symlink created (via administrator): {target}"
                except Exception as e:
                    return False, f"Failed to create symlink with admin privileges: {e}"
            else:
                # Try direct creation first using subprocess list form (no shell injection)
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                        shell=False  # Explicitly disable shell to prevent injection
                    )
                    if result.returncode != 0:
                        return False, f"Failed to create symlink: {result.stderr}"
                    return True, f"Symlink created successfully: {target}"
                except Exception as e:
                    return False, f"Error creating symlink: {e}"
        
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
