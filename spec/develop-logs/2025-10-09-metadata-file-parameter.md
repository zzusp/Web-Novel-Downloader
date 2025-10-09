# Metadata File Parameter for Commands

**Date**: 2025-10-09  
**Task**: download、replace、merge三个命令都新增必填参数，用来设置chapters_<hash>.json文件的路径，支持相对路径。执行时根据chapters_<hash>.json文件来处理

## Task Overview

Add a required `--metadata-file` parameter to the `download`, `replace`, and `merge` commands to specify which `chapters_<hash>.json` metadata file to use. This allows users to work with specific novels and ensures commands operate on the correct chapter files.

## Implementation Details

### Changes Made

1. **Updated CLI Argument Parsers**:
   - Added `--metadata-file` as required parameter to `download`, `replace`, and `merge` commands
   - Parameter supports both relative and absolute paths
   - Added helpful description for the parameter

2. **Enhanced Hash Extraction**:
   - Added `extract_hash_from_metadata_file()` function to extract hash from metadata file path
   - Supports filename-based extraction (chapters_<hash>.json)
   - Supports content-based extraction from menu_url in metadata
   - Handles both relative and absolute paths

3. **Updated File Finding Logic**:
   - Modified `find_chapter_files()` to accept optional `metadata_hash` parameter
   - When hash is provided, searches only in specific `chapters_<hash>/` directory
   - When hash is None, searches all `chapters_<hash>/` directories (backward compatibility)

4. **Updated Command Functions**:
   - Modified `replace_chapter_strings()` to accept `metadata_file` parameter
   - Modified `merge_chapters()` to accept `metadata_file` parameter
   - Updated `execute_download_command()` to use specified metadata file
   - Updated `execute_replace_command()` to pass metadata file to function
   - Updated `execute_merge_command()` to pass metadata file to function

### Command Usage Examples

**Download Command:**
```bash
./web-novel-downloader.exe download --metadata-file chapters/metadata/chapters_879584cc.json
```

**Replace Command:**
```bash
./web-novel-downloader.exe replace --metadata-file chapters/metadata/chapters_879584cc.json --string-replacements "[['old','new']]"
```

**Merge Command:**
```bash
./web-novel-downloader.exe merge --metadata-file chapters/metadata/chapters_879584cc.json --output novel.txt
```

### Technical Implementation

#### Hash Extraction Logic
```python
def extract_hash_from_metadata_file(metadata_file_path: str) -> str:
    # 1. Try to extract from filename (chapters_<hash>.json)
    # 2. If filename doesn't match, load file and extract from menu_url
    # 3. Fallback to filename without extension
```

#### File Finding Logic
```python
def find_chapter_files(pattern: str = "*.html", metadata_hash: str = None) -> List[Path]:
    if metadata_hash:
        # Search in specific chapters_<hash> subdirectory
        specific_dir = chapters_dir / f"chapters_{metadata_hash}"
        return list(specific_dir.glob(pattern))
    else:
        # Search in all chapters_<hash> subdirectories
        return all_chapter_files
```

### Benefits

- **Precise Control**: Users can specify exactly which novel's metadata to use
- **Multi-Novel Support**: Can work with different novels simultaneously
- **Path Flexibility**: Supports both relative and absolute paths
- **Backward Compatibility**: Maintains existing functionality for unspecified hash
- **Clear Organization**: Commands operate only on the specified novel's chapters

### Testing Results

- ✅ **Argument Parsing**: All three commands now require `--metadata-file` parameter
- ✅ **Hash Extraction**: Successfully extracts hash from various path formats
- ✅ **File Finding**: Correctly finds files in specific hash directories
- ✅ **Path Support**: Works with relative paths like `./chapters/metadata/chapters_879584cc.json`
- ✅ **Error Handling**: Proper error messages for invalid metadata files

## Next Steps

The implementation is complete and tested. All three commands now require the `--metadata-file` parameter and will operate only on the specified novel's chapters, providing precise control over which novel to work with.
