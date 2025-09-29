# Chapter Replace Command Implementation

**Date**: 2025-09-27  
**Task**: 额外给一个替换的命令吧，用来替换下载后的每个章节中的指定字符串

## Task Overview

Implement a replace command that:
1. Processes all downloaded chapter files in the chapters directory
2. Performs string replacements on chapter content
3. Supports batch processing of multiple chapters
4. Provides flexible replacement options

## Implementation Plan

### Phase 1: Add Replace Command Structure
- Add `replace` subcommand to argument parser
- Create replace command handler function
- Add command line arguments for replacement options

### Phase 2: Implement Replace Logic
- Create function to process individual chapter files
- Implement string replacement functionality
- Add support for multiple replacement patterns
- Handle file encoding and backup

### Phase 3: Add Advanced Features
- Support for regex replacements
- Backup original files before replacement
- Dry-run mode to preview changes
- Progress reporting

## Progress Log

### 2025-09-27 - Task Started
- Analyzed existing codebase structure
- Identified chapter file storage in `chapters/` directory
- Created implementation plan
- Started implementing replace command

### 2025-09-27 - Implementation Completed
- ✅ Added `replace` subcommand to argument parser
- ✅ Implemented `replace_chapter_strings` function with full functionality
- ✅ Added support for string and regex replacements
- ✅ Added case-sensitive/insensitive options
- ✅ Added backup functionality before replacement
- ✅ Added dry-run mode for previewing changes
- ✅ Added file pattern matching support
- ✅ Added comprehensive error handling and progress reporting

## Implementation Details

### New Features to Add

1. **Replace Command**
   - Process all HTML files in chapters directory
   - Support string and regex replacements
   - Batch processing with progress reporting

2. **Replacement Options**
   - String replacements: old -> new
   - Regex replacements with groups
   - Case-sensitive/insensitive options
   - Backup original files

3. **Safety Features**
   - Dry-run mode to preview changes
   - Backup creation before replacement
   - Rollback capability

## Technical Requirements

- Process all .html files in chapters directory
- Support both string and regex replacements
- Maintain file encoding (UTF-8)
- Provide progress feedback
- Handle errors gracefully
