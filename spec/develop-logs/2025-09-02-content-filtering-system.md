# Chapter Content Filtering System Implementation

**Date**: 2025-09-02  
**Task**: 下载章节内容时，通过章节内容的xpath匹配到的文本内容，希望可以再经过一遍正则的匹配，这个正则表达式为可选项；除追加正则表达式判断外，还希望可以支持传递字符串替换的数组，替换匹配结果（如果有正则表达式，则正则处理后的结果）中的某些字符，结构如：[["测试"，"test"],["A","a"]]

## Task Overview

Implement advanced content filtering for chapter downloads:
1. Add optional regex filtering for chapter content after XPath extraction
2. Implement string replacement functionality with configurable replacement pairs
3. Support both features in parse and download commands
4. Store filtering options in metadata for consistency

## Implementation Details

### New Features Added

1. **Regex Content Filtering**
   - Optional regex pattern to filter chapter content after XPath extraction
   - Supports regex groups and full matches
   - Clear feedback on match results
   - Error handling for invalid regex patterns

2. **String Replacement System**
   - Configurable string replacement pairs
   - JSON format: `[["old1","new1"],["old2","new2"]]`
   - Applied after regex filtering (if used)
   - Validation and error handling

3. **Enhanced Metadata Storage**
   - Stores regex patterns and string replacements in chapter metadata
   - Automatic loading of stored filtering options
   - Consistent filtering across parse and download operations

### Code Changes

#### NovelDownloader Class Updates

1. **Constructor Enhancement**:
   ```python
   def __init__(self, 
                chapter_xpath: str,
                content_xpath: str,
                concurrency: int = 3,
                proxy: Optional[str] = None,
                content_regex: Optional[str] = None,
                string_replacements: Optional[List[List[str]]] = None):
   ```

2. **New Content Processing Method**:
   ```python
   def _process_content(self, content: str) -> str:
       # Apply regex filtering if specified
       # Apply string replacements
       # Return processed content
   ```

3. **Enhanced Metadata Storage**:
   - Includes `content_regex` and `string_replacements` in saved metadata
   - Automatic loading of stored filtering options

#### Command Line Interface Updates

**New Arguments Added**:
- `--content-regex`: Optional regex pattern for content filtering
- `--string-replacements`: JSON string of replacement pairs

**Available for both commands**:
- `parse`: Store filtering options with chapter metadata
- `download`: Use filtering options for content processing

### Usage Examples

#### Basic Usage with Regex Filtering
```bash
# Parse with regex filtering
python novel_downloader.py parse "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter-link']" \
  --content-xpath "//div[@class='content']" \
  --content-regex "第.*?章.*?[\s\S]*?(?=第.*?章|$)"

# Download with same filtering
python novel_downloader.py download "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter-link']" \
  --content-xpath "//div[@class='content']" \
  --content-regex "第.*?章.*?[\s\S]*?(?=第.*?章|$)"
```

#### Advanced Usage with String Replacements
```bash
# Parse with both regex and string replacements
python novel_downloader.py parse "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter-link']" \
  --content-xpath "//div[@class='content']" \
  --content-regex "第.*?章.*?[\s\S]*?(?=第.*?章|$)" \
  --string-replacements "[['测试','test'],['A','a'],['　',' ']]"

# Download will automatically use stored filtering options
python novel_downloader.py download "https://example.com/novel" \
  --chapter-xpath "//a[@class='chapter-link']" \
  --content-xpath "//div[@class='content']"
```

#### String Replacements Format
```json
[
  ["old_string_1", "new_string_1"],
  ["old_string_2", "new_string_2"],
  ["　", " "],  // Replace full-width spaces with regular spaces
  ["测试", "test"]  // Replace Chinese characters
]
```

### Processing Flow

1. **XPath Extraction**: Extract content using specified XPath
2. **Regex Filtering** (if specified): Apply regex pattern to filter content
3. **String Replacements** (if specified): Replace specified strings
4. **Save Processed Content**: Store the final processed content

### Error Handling

- **Invalid Regex**: Clear error messages for malformed regex patterns
- **Invalid JSON**: Validation for string replacement format
- **No Matches**: Warning when regex finds no matches
- **Graceful Fallback**: Returns original content on processing errors

## Benefits

1. **Flexible Content Processing**: Regex and string replacement options
2. **Consistent Filtering**: Stored options ensure consistency across operations
3. **User-Friendly**: Clear feedback and error messages
4. **Backward Compatible**: All existing functionality preserved
5. **Configurable**: Optional features don't affect basic usage

## Progress Log

### 2025-09-02 - Implementation Completed
- ✅ Added regex content filtering functionality
- ✅ Implemented string replacement system
- ✅ Enhanced metadata storage with filtering options
- ✅ Updated command line interface for both commands
- ✅ Added comprehensive error handling and validation
- ✅ Created helper functions for JSON parsing
- ✅ Updated content processing pipeline
- ✅ Added emoji-enhanced status messages

## Technical Details

### Files Modified
- `novel_downloader.py`: Main implementation
- Enhanced `NovelDownloader` class with filtering capabilities
- Updated command line argument parsing
- Added content processing pipeline

### New Methods
- `_process_content()`: Main content processing method
- `parse_string_replacements()`: JSON parsing helper
- Enhanced metadata storage and loading

### Backward Compatibility
- All existing functionality preserved
- New features are optional
- No breaking changes to existing commands
