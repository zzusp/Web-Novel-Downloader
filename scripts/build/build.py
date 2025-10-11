#!/usr/bin/env python3
"""
Standard build script for Web Novel Downloader.
This script provides a unified interface for building packages and executables.
"""

import argparse
import subprocess
import sys
import platform
import re
import tempfile
import shutil
from pathlib import Path

def remove_path(path_pattern, description=""):
    """Remove files/directories matching pattern in a cross-platform way."""
    if description:
        print(f"\n[INFO] {description}")
    
    try:
        # Handle glob patterns
        if "*" in path_pattern:
            # Find all matching paths
            base_dir = Path(".")
            matching_paths = list(base_dir.glob(path_pattern))
            
            for path in matching_paths:
                if path.exists():
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"Removed directory: {path}")
                    else:
                        path.unlink()
                        print(f"Removed file: {path}")
        else:
            # Handle specific path
            path = Path(path_pattern)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed directory: {path}")
                else:
                    path.unlink()
                    print(f"Removed file: {path}")
        return True
    except Exception as e:
        print(f"[ERROR] Error removing {path_pattern}: {e}")
        return False

def run_command(cmd, description="", check=True):
    """Run a command and handle output."""
    if description:
        print(f"\n[INFO] {description}")
        print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error: {e}")
        if e.stdout:
            print("Stdout:", e.stdout)
        if e.stderr:
            print("Stderr:", e.stderr)
        return False

def validate_version(version):
    """Validate version format (semantic versioning)."""
    # Remove 'v' prefix if present
    if version.startswith('v'):
        version = version[1:]
    
    # Check if version matches semantic versioning pattern
    pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(pattern, version):
        raise ValueError(f"Invalid version format: {version}. Expected format: v0.0.1 or 0.0.1")
    
    return version

def update_version_in_file(file_path, version, pattern, replacement):
    """Update version in a file using regex pattern."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[SUCCESS] Updated version in {file_path}")
            return True
        else:
            print(f"[WARNING]  No version found to update in {file_path}")
            return False
    except Exception as e:
        print(f"[ERROR] Error updating {file_path}: {e}")
        return False

def update_version(version):
    """Update version in all relevant files."""
    print(f"Updating version to {version}...")
    
    # Validate version format
    try:
        version = validate_version(version)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return False
    
    success = True
    
    # Update pyproject.toml
    success &= update_version_in_file(
        "pyproject.toml",
        version,
        r'version = "[^"]*"',
        f'version = "{version}"'
    )
    
    # Update setup.py
    success &= update_version_in_file(
        "setup.py",
        version,
        r'version="[^"]*"',
        f'version="{version}"'
    )
    
    # Note: build_win.spec version parameter removed to avoid PyInstaller file path issues
    # Version information is now handled through the application itself
    
    # Update build_macos.spec
    success &= update_version_in_file(
        "build_macos.spec",
        version,
        r"'CFBundleVersion': '[^']*'",
        f"'CFBundleVersion': '{version}'"
    )
    
    success &= update_version_in_file(
        "build_macos.spec",
        version,
        r"'CFBundleShortVersionString': '[^']*'",
        f"'CFBundleShortVersionString': '{version}'"
    )
    
    if success:
        print(f"[SUCCESS] Version updated to {version} in all files")
    else:
        print(f"[ERROR] Some files failed to update version")
    
    return success

def build_packages():
    """Build Python packages (wheel and source distribution)."""
    print("[BUILD] Building Python packages...")
    
    # Clean previous builds
    remove_path("build/", "Cleaning build directory")
    remove_path("dist/", "Cleaning dist directory")
    remove_path("*.egg-info/", "Cleaning egg-info directories")
    
    # Try modern build first
    success = run_command([sys.executable, "-m", "build"], "Building packages with modern build")
    
    # If modern build fails, try traditional build
    if not success:
        print("[WARNING]  Modern build failed, trying traditional build...")
        success = run_command([sys.executable, "setup.py", "sdist", "bdist_wheel"], "Building packages with traditional build")
    
    if success:
        print("[SUCCESS] Python packages built successfully!")
        # Show generated files
        if Path("dist").exists():
            print("\nGenerated files:")
            for file in Path("dist").iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024*1024)
                    print(f"  - {file.name} ({size_mb:.1f} MB)")
    
    return success

def build_executable(platform_name, version="0.0.0"):
    """Build executable for specified platform."""
    if platform_name == "windows":
        spec_file = "build_win.spec"
        exe_name = f"web-novel-downloader-{version}.exe"
    elif platform_name == "macos":
        if platform.system() != "Darwin":
            print("[WARNING]  macOS build requires macOS system. Skipping...")
            return True
        spec_file = "build_macos.spec"
        exe_name = f"web-novel-downloader-{version}"
    else:
        print(f"[ERROR] Unsupported platform: {platform_name}")
        return False
    
    print(f"[BUILD] Building {platform_name} executable...")
    
    # Clean only PyInstaller build artifacts, preserve specs and scripts
    remove_path("build/book_downloader*", "Cleaning PyInstaller build artifacts")
    
    # Set environment variable for version
    import os
    os.environ['BUILD_VERSION'] = version
    
    # Build executable
    success = run_command(["pyinstaller", spec_file, "--clean"], f"Building {platform_name} executable")
    
    if success and Path(f"dist/{exe_name}").exists():
        size_mb = Path(f"dist/{exe_name}").stat().st_size / (1024*1024)
        print(f"[SUCCESS] {platform_name.title()} executable created: dist/{exe_name} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"[ERROR] Failed to create {platform_name} executable")
        return False

def test_executable():
    """Test the created executable."""
    current_platform = platform.system()
    if current_platform == "Windows":
        exe_path = "dist/web-novel-downloader.exe"
    elif current_platform == "Darwin":
        exe_path = "dist/web-novel-downloader"
    else:
        print(f"[WARNING]  Unsupported platform for testing: {current_platform}")
        return True
    
    if not Path(exe_path).exists():
        print(f"[ERROR] Executable not found: {exe_path}")
        return False
    
    print("[TEST] Testing executable...")
    success = run_command([exe_path, "--help"], "Testing executable help command")
    
    if success:
        print("[SUCCESS] Executable test passed!")
    else:
        print("[ERROR] Executable test failed!")
    
    return success

def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build Web Novel Downloader")
    parser.add_argument("--packages", action="store_true", help="Build Python packages")
    parser.add_argument("--exe", choices=["windows", "macos", "all"], help="Build executable(s)")
    parser.add_argument("--test", action="store_true", help="Test executable after building")
    parser.add_argument("--all", action="store_true", help="Build everything")
    parser.add_argument("--version", type=str, help="Set version number (e.g., v0.0.1 or 0.0.1)")
    parser.add_argument("--version-only", action="store_true", help="Only update version, don't build")
    
    args = parser.parse_args()
    
    # Handle version update
    current_version = "0.0.0"
    if args.version:
        if not update_version(args.version):
            print("[ERROR] Version update failed!")
            return 1
        
        # Extract version number for executable naming
        current_version = validate_version(args.version)
        
        if args.version_only:
            print("[SUCCESS] Version updated successfully!")
            return 0
    
    if not any([args.packages, args.exe, args.all]):
        parser.print_help()
        return 1
    
    success = True
    
    if args.all or args.packages:
        success &= build_packages()
    
    if args.all or args.exe:
        if args.exe == "all" or args.all:
            success &= build_executable("windows", current_version)
            if platform.system() == "Darwin":
                success &= build_executable("macos", current_version)
        else:
            success &= build_executable(args.exe, current_version)
    
    if args.test and success:
        success &= test_executable()
    
    if success:
        print("\n[SUCCESS] Build completed successfully!")
    else:
        print("\n[ERROR] Build failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
