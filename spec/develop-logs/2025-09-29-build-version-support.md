# Build System Version Number Support Task

**Date**: 2025-09-29  
**Task**: Add version number support to build system (v0.0.1 format)  
**Status**: In Progress

## Problem Analysis

The current build system has hardcoded version numbers in multiple places:
1. `pyproject.toml` - version = "1.0.0"
2. `setup.py` - version = "1.0.0"  
3. `build_macos.spec` - CFBundleVersion and CFBundleShortVersionString = "1.0.0"
4. `build_win.spec` - version = None (not set)

Need to add support for setting version numbers like v0.0.1 through build script parameters.

## Current Build System Analysis

### Files with version information:
- **pyproject.toml**: Line 7 - `version = "1.0.0"`
- **setup.py**: Line 22 - `version = "1.0.0"`
- **build_macos.spec**: Lines 125-126 - CFBundleVersion and CFBundleShortVersionString
- **build_win.spec**: Line 112 - `version=None` (not set)

### Build script:
- **scripts/build/build.py**: Main build script that needs to accept version parameter

## Implementation Plan

1. ✅ Analyze current build system and version locations
2. ⏳ Update build script to accept --version parameter
3. ⏳ Create version update function to modify version in all files
4. ⏳ Update PyInstaller spec files to use dynamic version
5. ⏳ Test version build functionality
6. ⏳ Update documentation

## Technical Approach

### Version Parameter Format
- Accept version in format: `v0.0.1` or `0.0.1`
- Strip 'v' prefix if present
- Validate version format (semantic versioning)

### Files to Update
1. **pyproject.toml**: Update `version = "X.X.X"`
2. **setup.py**: Update `version = "X.X.X"`
3. **build_win.spec**: Update `version='X.X.X'`
4. **build_macos.spec**: Update CFBundleVersion and CFBundleShortVersionString

### Build Script Changes
- Add `--version` argument to argparse
- Create `update_version()` function
- Call version update before building
- Support both temporary (build-time) and permanent version updates

## Progress Log

- **2025-09-29**: Task started, analyzed current build system
- **2025-09-29**: Identified all files containing version information
- **2025-09-29**: Created implementation plan
- **2025-09-29**: Implemented version update functions in build script
- **2025-09-29**: Added --version and --version-only parameters to build script
- **2025-09-29**: Fixed regex patterns for accurate version replacement
- **2025-09-29**: Tested version update functionality successfully
- **2025-09-29**: Tested building packages with version parameter successfully

## Implementation Details

### New Build Script Features
- `--version v0.0.1` or `--version 0.0.1`: Set version number (supports both formats)
- `--version-only`: Only update version without building
- Version validation using semantic versioning pattern
- Automatic 'v' prefix removal if present

### Files Updated
- **pyproject.toml**: `version = "X.X.X"`
- **setup.py**: `version="X.X.X"`
- **build_win.spec**: `version="X.X.X"`
- **build_macos.spec**: `CFBundleVersion` and `CFBundleShortVersionString`

### Usage Examples
```bash
# Update version only
python scripts/build/build.py --version v0.1.0 --version-only

# Build packages with version
python scripts/build/build.py --version v0.1.0 --packages

# Build executables with version
python scripts/build/build.py --version v0.1.0 --exe windows

# Build everything with version
python scripts/build/build.py --version v0.1.0 --all
```

## Testing Results
- ✅ Version update works correctly for all files
- ✅ Version validation works (rejects invalid formats)
- ✅ Package building with version works correctly
- ✅ Generated packages have correct version numbers
