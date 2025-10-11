# Parse Command Hash Parameter Implementation

**Date**: 2025-10-11  
**Task**: Add --hash parameter to parse command to support setting custom hash values in `chapters_<hash>.json` files

## Overview

The parse command currently generates metadata files with hash values based on the MD5 hash of the menu URL. This task adds a new `--hash` parameter that allows users to specify a custom hash value for the metadata file, providing more control over file naming and organization.

## Current Implementation Analysis

### Current Hash Generation
- Hash is generated in `MetadataManager._generate_metadata_filename()` using MD5 of menu URL
- Format: `chapters_{hash}.json` where hash is first 8 characters of MD5
- Used for organizing downloaded chapters in `chapters_{hash}/` subdirectories

### Files to Modify
1. `src/book_downloader/cli.py` - Add --hash parameter to parse command
2. `src/book_downloader/metadata.py` - Modify MetadataManager to support custom hash
3. `src/book_downloader/core.py` - Update parse command execution

## Implementation Plan

### Phase 1: CLI Parameter Addition
- [x] Add `--hash` parameter to parse command in `create_argument_parser()`
- [x] Make parameter optional with validation
- [x] Pass hash value to parse command execution

### Phase 2: MetadataManager Updates
- [ ] Modify `_generate_metadata_filename()` to accept custom hash
- [ ] Update `save_chapter_metadata()` to use custom hash when provided
- [ ] Ensure backward compatibility with existing functionality

### Phase 3: Core Integration
- [ ] Update `execute_parse_command()` to pass hash parameter
- [ ] Modify `parse_chapters()` method to accept and use custom hash
- [ ] Test integration with existing download/merge commands

### Phase 4: Testing and Documentation
- [ ] Test with custom hash values
- [ ] Verify compatibility with existing commands
- [ ] Update usage documentation

## Technical Details

### Hash Parameter Validation
- Should be alphanumeric (letters, numbers, underscores, hyphens)
- Length: 1-32 characters (reasonable limit)
- Must be unique to avoid conflicts

### Backward Compatibility
- Default behavior unchanged when --hash not provided
- Existing metadata files continue to work
- Download/merge commands work with both old and new hash formats

## Progress Log

### 2025-10-11 - Initial Analysis
- Analyzed current hash generation mechanism
- Identified files requiring modification
- Created implementation plan
- Started with CLI parameter addition

### 2025-10-11 - Implementation Complete
- ✅ Added --hash parameter to parse command in CLI
- ✅ Updated MetadataManager to support custom hash values
- ✅ Modified NovelDownloader to accept and use custom hash
- ✅ Updated all related methods to pass custom hash through the system
- ✅ Added hash validation (1-32 characters, alphanumeric + underscore + hyphen)
- ✅ Tested functionality with comprehensive test cases
- ✅ Verified backward compatibility (existing functionality unchanged)

### Implementation Details
- Hash validation regex: `^[a-zA-Z0-9_-]{1,32}$`
- Custom hash takes precedence over URL-based hash when provided
- All metadata operations (save, load, get_stored_chapters) support custom hash
- Download and merge commands work with both old and new hash formats
- Error handling for invalid hash values with clear user feedback

### 2025-10-11 - Documentation Complete
- ✅ Updated USAGE_GUIDE.md with detailed --hash parameter documentation
- ✅ Added parameter explanation, usage scenarios, and requirements
- ✅ Included practical examples with custom hash values
- ✅ Updated output examples to show both default and custom hash scenarios
- ✅ Marked task as completed in development-progress.md

### Task Status: COMPLETED ✅

The --hash parameter has been successfully implemented and documented. Users can now specify custom hash values for metadata file naming, providing better control over file organization and management.
