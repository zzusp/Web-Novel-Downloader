# Package Name Change Task

**Date**: 2025-09-29  
**Task**: Change package name prefix from book_downloader to web-novel-downloader  
**Status**: In Progress

## Problem Analysis

The current package naming uses "book_downloader" as the prefix, but the user wants to change it to "web-novel-downloader" for better branding and consistency.

## Current Package Naming Analysis

### Files containing "book_downloader":
- **pyproject.toml**: Package name and entry points
- **setup.py**: Package name and entry points  
- **build_macos.spec**: Bundle identifier and executable name
- **build_win.spec**: Executable name
- **scripts/build/build.py**: Build script references
- **README.md**: Documentation references
- **docs/**: Documentation files
- **tests/**: Test files
- **scripts/**: Script files
- **MANIFEST.in**: Manifest file

### Current naming patterns:
- Package name: `book_downloader`
- Executable name: `book-downloader`
- Bundle identifier: `com.bookdownloader.app`
- Entry points: `book-downloader`, `book-scraper`

## Target naming patterns:
- Package name: `web-novel-downloader`
- Executable name: `web-novel-downloader`
- Bundle identifier: `com.webnoveldownloader.app`
- Entry points: `web-novel-downloader`, `web-novel-scraper`

## Implementation Plan

1. ✅ Analyze current package naming in all files
2. ⏳ Update package names in configuration files
3. ⏳ Update executable names in spec files
4. ⏳ Update entry points and script references
5. ⏳ Update documentation references
6. ⏳ Test package build with new naming

## Progress Log

- **2025-09-29**: Task started, analyzed current package naming
- **2025-09-29**: Identified all files containing package references
- **2025-09-29**: Created implementation plan
- **2025-09-29**: Updated package names in all configuration files
- **2025-09-29**: Updated executable names in PyInstaller spec files
- **2025-09-29**: Updated entry points and script references
- **2025-09-29**: Updated README.md with new executable names
- **2025-09-29**: Tested package build with new naming successfully

## Changes Made

### Configuration Files Updated
- **pyproject.toml**: 
  - Package name: `book-downloader` → `web-novel-downloader`
  - Entry points: `book-downloader` → `web-novel-downloader`, `book-scraper` → `web-novel-scraper`
- **setup.py**: 
  - Package name: `Web-Novel-Downloader` → `web-novel-downloader`
  - Entry points: Updated to match pyproject.toml
- **build_win.spec**: 
  - Executable name: `book-downloader` → `web-novel-downloader`
- **build_macos.spec**: 
  - Executable name: `book-downloader` → `web-novel-downloader`
  - App name: `book-downloader.app` → `web-novel-downloader.app`
  - Bundle identifier: `com.bookdownloader.app` → `com.webnoveldownloader.app`
  - Display names: `Book Downloader` → `Web Novel Downloader`

### Build Script Updated
- **scripts/build/build.py**: Updated executable paths and names

### Documentation Updated
- **README.md**: Updated all command examples to use new executable names

## Testing Results
- ✅ Package build works correctly with new naming
- ✅ Generated packages have correct names: `web_novel_downloader-0.4.0`
- ✅ Entry points work correctly: `web-novel-downloader`, `web-novel-scraper`
- ✅ All command examples in README updated
