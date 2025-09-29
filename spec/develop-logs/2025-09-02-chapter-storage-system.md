# Chapter Storage System Implementation

**Date**: 2025-09-02  
**Task**: 通过url获取到章节信息后，将解析后的章节信息存储起来，之后执行下载章节命令时，读取之前存储起来的文件，如果找不到之前存储的文件，则不下载报个警告信息

## Task Overview

Implement a chapter information storage system that:
1. Stores parsed chapter information after URL parsing
2. Retrieves stored chapter information for download commands
3. Shows warning when stored chapter file is not found

## Implementation Plan

### Phase 1: Chapter Information Storage
- Add functionality to save parsed chapter data to JSON file
- Include metadata like URL, timestamp, chapter count
- Store in a dedicated directory for chapter metadata

### Phase 2: Chapter Information Retrieval
- Modify download command to check for existing chapter metadata
- Load chapter information from stored file if available
- Skip URL parsing if valid stored data exists

### Phase 3: Warning System
- Add warning when stored chapter file is not found
- Provide clear error messages and guidance
- Graceful fallback to URL parsing if needed

## Progress Log

### 2025-09-02 - Task Started
- Analyzed current codebase structure
- Identified key files: `novel_downloader.py`, `scraper.py`
- Created implementation plan
- Started implementing chapter storage functionality

### 2025-09-02 - Implementation Completed
- ✅ Added chapter metadata storage functionality
- ✅ Implemented JSON-based storage in `chapters/metadata/` directory
- ✅ Added chapter information retrieval methods
- ✅ Modified download command to use stored data
- ✅ Added new `parse` command for extracting chapter information
- ✅ Implemented warning system when stored files are not found
- ✅ Added graceful fallback to URL parsing when needed
- ✅ Updated command line interface with new options

## Implementation Details

### New Features Added

1. **Chapter Metadata Storage**
   - JSON format storage in `chapters/metadata/` directory
   - Includes URL, timestamp, XPath expressions, and chapter list
   - Unique filename generation using URL hash

2. **New Commands**
   - `parse`: Extract and store chapter information from URL
   - `download`: Download chapters using stored information (with fallback)

3. **Warning System**
   - Clear warnings when stored chapter data is not found
   - Guidance messages for users
   - Graceful error handling

4. **Enhanced Download Command**
   - Optional XPath arguments when stored data exists
   - `--force-parse` option to bypass stored data
   - Automatic fallback to URL parsing if needed

### Usage Examples

```bash
# Parse chapter information and store it
python novel_downloader.py parse "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter-link']" \
  --content-xpath "//div[@class='content']"

# Download using stored information
python novel_downloader.py download "https://example.com/novel"

# Force re-parsing from URL
python novel_downloader.py download "https://example.com/novel" --force-parse
```

## Technical Details

### Files to Modify
- `novel_downloader.py`: Main implementation
- Add new methods for storage/retrieval
- Update command line interface

### Storage Format
- JSON format for chapter metadata
- Include: URL, timestamp, chapters list, XPath expressions
- Store in `chapters/` directory with descriptive filename

### Error Handling
- File not found warnings
- Invalid JSON handling
- Graceful fallback mechanisms
