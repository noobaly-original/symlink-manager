#!/usr/bin/env python3
"""
Build script to create standalone executables for Symlink Manager.
Supports Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def get_platform():
    """Get the current platform."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def convert_png_to_ico(png_path="symlink_manager_icon.png", ico_path="symlink_manager_icon.ico"):
    """Convert the PNG icon to .ico format for Windows executables using Pillow."""
    try:
        from PIL import Image
        img = Image.open(png_path)
        # Save as .ico with multiple sizes for better quality
        img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"✅ Converted {png_path} -> {ico_path}")
        return True
    except ImportError:
        print("⚠️ Pillow not installed. Install it with: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Failed to convert icon: {e}")
        return False


def clean_build_dirs():
    """Remove previous build artifacts."""
    dirs_to_remove = ["build", "dist", "__pycache__", "*.egg-info"]
    
    for pattern in dirs_to_remove:
        if pattern.endswith("*"):
            # Handle glob patterns
            for item in Path(".").glob(pattern):
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"Removed: {item}")
        else:
            path = Path(pattern)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed: {path}")
                else:
                    path.unlink()
                    print(f"Removed: {path}")


def build_macos():
    """Build macOS app bundle."""
    print("🍎 Building macOS executable...")
    
    cmd = [
        ".venv/bin/pyinstaller",
        "symlink_app.spec",
        "--distpath=dist",
        "--workpath=build",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ macOS build successful!")
        print("📦 Output: dist/SymlinkManager.app")
        print("\nTo run the app:")
        print("  open dist/SymlinkManager.app")
        return True
    else:
        print("❌ macOS build failed!")
        print("STDERR:", result.stderr)
        return False


def build_windows():
    """Build Windows executable."""
    print("🪟 Building Windows executable...")
    
    # Convert PNG to ICO for Windows executable icon
    if not convert_png_to_ico():
        print("⚠️ Continuing without .ico conversion...")
    
    cmd = [
        ".venv\\Scripts\\pyinstaller.exe",
        "symlink_app.spec",
        "--distpath=dist",
        "--workpath=build",
    ]
    
    # Use shell=False to prevent command injection (safer subprocess usage)
    result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    
    if result.returncode == 0:
        print("✅ Windows build successful!")
        print("📦 Output: dist\\SymlinkManager.exe")
        return True
    else:
        print("❌ Windows build failed!")
        print("STDERR:", result.stderr)
        return False


def build_linux():
    """Build Linux executable."""
    print("🐧 Building Linux executable...")
    
    cmd = [
        ".venv/bin/pyinstaller",
        "--onefile",
        "--windowed",
        "--name=SymlinkManager",
        "--distpath=dist",
        "--workpath=build",
        "app.py",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Linux build successful!")
        print("📦 Output: dist/SymlinkManager")
        print("\nTo run the app:")
        print("  chmod +x dist/SymlinkManager")
        print("  ./dist/SymlinkManager")
        return True
    else:
        print("❌ Linux build failed!")
        print("STDERR:", result.stderr)
        return False


def main():
    """Main build function."""
    print("=" * 60)
    print("  Symlink Manager - Executable Builder")
    print("=" * 60)
    
    current_platform = get_platform()
    print(f"\n🔍 Detected platform: {current_platform.upper()}\n")
    
    # Check if .venv exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please create it with: uv venv")
        return False
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    clean_build_dirs()
    print()
    
    # Build for the current platform
    if current_platform == "macos":
        success = build_macos()
    elif current_platform == "windows":
        success = build_windows()
    elif current_platform == "linux":
        success = build_linux()
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Build completed successfully!")
        print("=" * 60)
        return True
    else:
        print("❌ Build failed!")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
