#!/usr/bin/env python3
"""
Standard build script for Web Novel Downloader.
This script provides a unified interface for building packages and executables.
"""

import argparse
import subprocess
import sys
import platform
from pathlib import Path

def run_command(cmd, description="", check=True):
    """Run a command and handle output."""
    if description:
        print(f"\n🔄 {description}")
        print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False

def build_packages():
    """Build Python packages (wheel and source distribution)."""
    print("📦 Building Python packages...")
    
    # Clean previous builds
    run_command(["rm", "-rf", "build/", "dist/", "*.egg-info/"], "Cleaning build artifacts")
    
    # Try modern build first
    success = run_command([sys.executable, "-m", "build"], "Building packages with modern build")
    
    # If modern build fails, try traditional build
    if not success:
        print("⚠️  Modern build failed, trying traditional build...")
        success = run_command([sys.executable, "setup.py", "sdist", "bdist_wheel"], "Building packages with traditional build")
    
    if success:
        print("✅ Python packages built successfully!")
        # Show generated files
        if Path("dist").exists():
            print("\nGenerated files:")
            for file in Path("dist").iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024*1024)
                    print(f"  - {file.name} ({size_mb:.1f} MB)")
    
    return success

def build_executable(platform_name):
    """Build executable for specified platform."""
    if platform_name == "windows":
        spec_file = "build_win.spec"
        exe_name = "book-downloader.exe"
    elif platform_name == "macos":
        if platform.system() != "Darwin":
            print("⚠️  macOS build requires macOS system. Skipping...")
            return True
        spec_file = "build_macos.spec"
        exe_name = "book-downloader"
    else:
        print(f"❌ Unsupported platform: {platform_name}")
        return False
    
    print(f"🔨 Building {platform_name} executable...")
    
    # Clean only PyInstaller build artifacts, preserve specs and scripts
    run_command(["rm", "-rf", "build/book_downloader*"], "Cleaning PyInstaller build artifacts")
    
    # Build executable
    success = run_command(["pyinstaller", spec_file, "--clean"], f"Building {platform_name} executable")
    
    if success and Path(f"dist/{exe_name}").exists():
        size_mb = Path(f"dist/{exe_name}").stat().st_size / (1024*1024)
        print(f"✅ {platform_name.title()} executable created: dist/{exe_name} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"❌ Failed to create {platform_name} executable")
        return False

def test_executable():
    """Test the created executable."""
    current_platform = platform.system()
    if current_platform == "Windows":
        exe_path = "dist/book-downloader.exe"
    elif current_platform == "Darwin":
        exe_path = "dist/book-downloader"
    else:
        print(f"⚠️  Unsupported platform for testing: {current_platform}")
        return True
    
    if not Path(exe_path).exists():
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    print("🧪 Testing executable...")
    success = run_command([exe_path, "--help"], "Testing executable help command")
    
    if success:
        print("✅ Executable test passed!")
    else:
        print("❌ Executable test failed!")
    
    return success

def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build Web Novel Downloader")
    parser.add_argument("--packages", action="store_true", help="Build Python packages")
    parser.add_argument("--exe", choices=["windows", "macos", "all"], help="Build executable(s)")
    parser.add_argument("--test", action="store_true", help="Test executable after building")
    parser.add_argument("--all", action="store_true", help="Build everything")
    
    args = parser.parse_args()
    
    if not any([args.packages, args.exe, args.all]):
        parser.print_help()
        return 1
    
    success = True
    
    if args.all or args.packages:
        success &= build_packages()
    
    if args.all or args.exe:
        if args.exe == "all" or args.all:
            success &= build_executable("windows")
            if platform.system() == "Darwin":
                success &= build_executable("macos")
        else:
            success &= build_executable(args.exe)
    
    if args.test and success:
        success &= test_executable()
    
    if success:
        print("\n🎉 Build completed successfully!")
    else:
        print("\n❌ Build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
