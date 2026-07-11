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
    """Convert the PNG icon to .ico format with proper BMP DIB encoding for Windows.

    Unlike Pillow's built-in ICO saving (which uses PNG compression for larger sizes
    and looks blurry/pixelated on Windows), this manually constructs the ICO with
    32-bit BGRA BMP DIB entries + 1-bit AND masks for every size. This is the format
    Windows Explorer renders best.
    """
    try:
        from PIL import Image
        import struct

        img = Image.open(png_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        orig_w, orig_h = img.size
        print(f"ℹ️  Original icon size: {orig_w}x{orig_h}")

        # Standard Windows icon sizes — include all that fit within the original
        all_sizes = [
            (16, 16), (24, 24), (32, 32), (48, 48),
            (64, 64), (96, 96), (128, 128), (256, 256),
        ]
        icon_sizes = [(w, h) for w, h in all_sizes if w <= orig_w and h <= orig_h]

        if not icon_sizes:
            icon_sizes = [(orig_w, orig_h)]

        # Downscale with high-quality Lanczos resampling
        images = []
        for size in icon_sizes:
            if size == (orig_w, orig_h):
                images.append(img.copy())
            else:
                images.append(img.resize(size, Image.LANCZOS))

        # ----------------------------------------------------------------
        # Build the ICO file manually — every entry is BMP DIB (not PNG)
        # ----------------------------------------------------------------
        dir_entries = []

        for pil_img in images:
            w, h = pil_img.size
            pixels = list(pil_img.getdata())

            # --- XOR mask: 32-bit BGRA pixels, stored bottom-up ---
            xor_row_size = w * 4  # 4 bytes per pixel, already 4-byte aligned
            xor_mask = b''
            for y in range(h - 1, -1, -1):
                row = b''
                for x in range(w):
                    r, g, b, a = pixels[y * w + x]
                    row += struct.pack('BBBB', b, g, r, a)  # Windows: BGRA order
                xor_mask += row

            # --- AND mask: 1-bit transparency mask, stored bottom-up ---
            #    Bit = 0 → draw pixel (use XOR data)
            #    Bit = 1 → transparent
            #    First pixel → MSB of first byte
            and_row_bytes = (w + 7) // 8
            and_row_padded = ((w + 31) // 32) * 4  # padded to DWORD boundary
            and_mask = b''
            for y in range(h - 1, -1, -1):
                raw_row = b''
                for x in range(w):
                    _, _, _, a = pixels[y * w + x]
                    if x % 8 == 0:
                        byte_val = 0
                    if a < 128:  # treat as transparent
                        byte_val |= (1 << (7 - (x % 8)))
                    if x % 8 == 7 or x == w - 1:
                        raw_row += bytes([byte_val])
                # Pad row to 4-byte boundary
                raw_row += b'\x00' * (and_row_padded - len(raw_row))
                and_mask += raw_row

            # --- BITMAPINFOHEADER (40 bytes) ---
            image_data_size = xor_row_size * h + and_row_padded * h
            bih = struct.pack('<IiiHHIIiiII',
                40,                 # biSize
                w,                  # biWidth
                h * 2,              # biHeight = 2×h (XOR mask + AND mask combined)
                1,                  # biPlanes
                32,                 # biBitCount
                0,                  # biCompression (BI_RGB)
                image_data_size,    # biSizeImage
                0, 0, 0, 0,         # biXPelsPerMeter, biYPelsPerMeter, biClrUsed, biClrImportant
            )

            bmp_data = bih + xor_mask + and_mask
            dir_entries.append({
                'width': w if w < 256 else 0,   # 0 in the directory means 256
                'height': h if h < 256 else 0,
                'data': bmp_data,
            })

        # --- ICO file header (6 bytes) ---
        count = len(dir_entries)
        ico_data = struct.pack('<HHH', 0, 1, count)  # reserved, type=1 (icon), count

        # --- Directory entries (16 bytes each) ---
        offset = 6 + 16 * count
        for entry in dir_entries:
            data = entry['data']
            ico_data += struct.pack('<BBBBHHII',
                entry['width'],     # width (0 = 256)
                entry['height'],    # height (0 = 256)
                0,                  # colors in palette (0 = no palette)
                0,                  # reserved
                1,                  # color planes
                32,                 # bits per pixel
                len(data),          # bytes in this entry's data
                offset,             # offset from start of file
            )
            offset += len(data)

        # --- Image data blocks ---
        for entry in dir_entries:
            ico_data += entry['data']

        with open(ico_path, 'wb') as f:
            f.write(ico_data)

        print(f"✅ Converted {png_path} -> {ico_path} ({count} BMP DIB sizes: {icon_sizes})")
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
