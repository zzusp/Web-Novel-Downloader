#!/usr/bin/env python3
"""
Book Downloader - A tool for downloading novels from web pages with configurable XPath expressions.

This package provides functionality to:
- Parse chapter lists from web pages using XPath expressions
- Download novel chapters with concurrent processing
- Handle pagination for both chapter lists and individual chapters
- Process content with regex filtering and string replacements
- Generate EPUB and TXT output formats
- Manage chapter metadata and provide resume functionality
"""

__version__ = "1.0.0"
__author__ = "Book Downloader Team"
__email__ = "book-downloader@example.com"

from .core import NovelDownloader
from .config import (
    chapters_dir,
    metadata_dir,
    temp_dir,
    DEFAULT_CONCURRENCY,
    DEFAULT_OUTPUT_FILE,
    DEFAULT_NOVEL_TITLE,
    DEFAULT_AUTHOR,
    DEFAULT_FORMAT,
    DEFAULT_FILE_PATTERN,
    CLOUDFLARE_MAX_WAIT_TIME,
    CLOUDFLARE_CHECK_INTERVAL,
)
from .utils import (
    parse_string_replacements,
    process_content_with_regex,
    apply_string_replacements,
    sanitize_filename,
    extract_chapter_title,
    sort_chapters_by_metadata,
)
from .metadata import (
    MetadataManager,
    find_metadata_files,
    load_metadata_from_file,
    find_best_metadata,
)
from .epub_generator import create_epub

__all__ = [
    # Main classes
    "NovelDownloader",
    "MetadataManager",
    
    # Configuration
    "chapters_dir",
    "metadata_dir", 
    "temp_dir",
    "DEFAULT_CONCURRENCY",
    "DEFAULT_OUTPUT_FILE",
    "DEFAULT_NOVEL_TITLE",
    "DEFAULT_AUTHOR",
    "DEFAULT_FORMAT",
    "DEFAULT_FILE_PATTERN",
    "CLOUDFLARE_MAX_WAIT_TIME",
    "CLOUDFLARE_CHECK_INTERVAL",
    
    # Utility functions
    "parse_string_replacements",
    "process_content_with_regex",
    "apply_string_replacements",
    "sanitize_filename",
    "extract_chapter_title",
    "sort_chapters_by_metadata",
    
    # Metadata functions
    "find_metadata_files",
    "load_metadata_from_file",
    "find_best_metadata",
    
    # EPUB generation
    "create_epub",
]
