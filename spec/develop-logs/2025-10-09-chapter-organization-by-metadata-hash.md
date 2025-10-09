# Chapter Organization by Metadata Hash

**Date**: 2025-10-09  
**Task**: 现在download命令下载的所有小说的章节内容都在 @chapters/ 目录下，无法区分章节来自哪个chapters_<hash>.json文件，所以希望可以区分一下，download时，不同的chapters_<hash>.json文件下载到的对应的chapters_<hash>目录

## Task Overview

Currently, all downloaded chapters are stored directly in the `chapters/` directory, making it impossible to distinguish which chapters belong to which metadata file. The goal is to organize chapters by their source metadata hash, creating separate directories for each novel.

## Current Structure Analysis

- **Current**: All chapters stored in `chapters/` directory
- **Metadata files**: Stored in `chapters/metadata/` with format `chapters_<hash>.json`
- **Problem**: No way to distinguish which chapters belong to which metadata file
- **Goal**: Create `chapters_<hash>/` directories for each metadata file

## Implementation Plan

### Phase 1: Modify Download Chapter Method
- Update `download_chapter` method to accept metadata hash parameter
- Create subdirectory based on metadata hash
- Store chapters in `chapters_<hash>/` instead of `chapters/`

### Phase 2: Update Metadata Manager
- Modify metadata manager to provide hash information
- Update download workflow to pass hash to download method

### Phase 3: Update Core Download Logic
- Modify `download_novel` method to extract hash from metadata
- Pass hash information to individual chapter downloads

## Progress Log

### 2025-10-09 - Task Started
- Analyzed current chapter storage structure
- Identified that chapters are stored directly in `chapters/` directory
- Found that metadata files use hash-based naming: `chapters_<hash>.json`
- Created implementation plan for organizing chapters by hash

### 2025-10-09 - Implementation Completed
- ✅ Updated development progress file
- ✅ Modified download_chapter method to accept metadata_hash parameter
- ✅ Added hash extraction methods to MetadataManager
- ✅ Updated download_novel method to pass metadata hash to chapter downloads
- ✅ Tested the new organization system successfully
- ✅ Verified directory creation and hash extraction functionality
- ✅ Updated replace command to work with new chapter organization
- ✅ Updated merge command to work with new chapter organization
- ✅ Tested both commands with new directory structure

## Technical Details

### Current Chapter Storage
```python
# Current: chapters_dir / f"{safe_title}.html"
chapter_file = chapters_dir / f"{safe_title}.html"
```

### Proposed Chapter Storage
```python
# Proposed: chapters_dir / f"chapters_{hash}" / f"{safe_title}.html"
hash_dir = chapters_dir / f"chapters_{hash}"
hash_dir.mkdir(exist_ok=True)
chapter_file = hash_dir / f"{safe_title}.html"
```

### Directory Structure
```
chapters/
├── metadata/
│   └── chapters_879584cc.json
├── chapters_879584cc/          # New: organized by hash
│   ├── 第1章 楔子 繁华过眼开一季.html
│   ├── 第2章 苏家赘婿.html
│   └── ...
└── chapters_<other_hash>/      # Future: other novels
    └── ...
```

## Implementation Summary

### Changes Made

1. **Modified `download_chapter` method** in `src/book_downloader/core.py`:
   - Added `metadata_hash` parameter with default value `None`
   - Added logic to create `chapters_<hash>/` subdirectory when hash is provided
   - Maintained backward compatibility for existing code

2. **Enhanced `MetadataManager`** in `src/book_downloader/metadata.py`:
   - Added `_extract_hash_from_filename()` method to extract hash from metadata filename
   - Added `get_metadata_hash()` method to get hash for a given menu URL
   - Maintained existing functionality while adding new capabilities

3. **Updated `download_novel` method** in `src/book_downloader/core.py`:
   - Added metadata hash retrieval before starting downloads
   - Modified chapter download calls to pass metadata hash
   - Added informative messages about directory organization

4. **Enhanced CLI commands** in `src/book_downloader/cli.py`:
   - Added `find_chapter_files()` function to search only `chapters_<hash>/` subdirectories
   - Updated `replace_chapter_strings()` to use new file finding logic
   - Updated `merge_chapters()` to use new file finding logic
   - Enhanced backup functionality to preserve directory structure
   - Simplified logic by removing backward compatibility with old main directory files

### Directory Structure

**Before:**
```
chapters/
├── metadata/
│   └── chapters_879584cc.json
├── 第1章 楔子 繁华过眼开一季.html
├── 第2章 苏家赘婿.html
└── ...
```

**After:**
```
chapters/
├── metadata/
│   └── chapters_879584cc.json
├── chapters_879584cc/          # Organized by metadata hash
│   ├── 第1章 楔子 繁华过眼开一季.html
│   ├── 第2章 苏家赘婿.html
│   └── ...
└── chapters_<other_hash>/      # Other novels
    └── ...
```

### Benefits

- **Clear Organization**: Chapters are now organized by their source metadata file
- **No Conflicts**: Different novels won't have conflicting chapter files
- **Scalable**: Supports multiple novels with separate directories
- **User-Friendly**: Clear directory structure makes it easy to identify chapter sources
- **Simplified Logic**: Commands only work with organized chapter structure

## Next Steps

The implementation is complete and tested. The new chapter organization system is ready for use. Future downloads will automatically organize chapters by their metadata hash, providing clear separation between different novels.
