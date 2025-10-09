"""
Tests for configuration module.
"""

import pytest
from pathlib import Path
from src.book_downloader.config import (
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


class TestConfig:
    """Test configuration constants and directories."""
    
    def test_directories_exist(self):
        """Test that required directories exist."""
        assert chapters_dir.exists()
        assert metadata_dir.exists()
        assert Path(temp_dir).exists()
    
    def test_default_values(self):
        """Test default configuration values."""
        assert DEFAULT_CONCURRENCY == 3
        assert DEFAULT_OUTPUT_FILE == "novel.txt"
        assert DEFAULT_NOVEL_TITLE == "Downloaded Novel"
        assert DEFAULT_AUTHOR == "Unknown"
        assert DEFAULT_FORMAT == "txt"
        assert DEFAULT_FILE_PATTERN == "*.html"
        assert CLOUDFLARE_MAX_WAIT_TIME == 120
        assert CLOUDFLARE_CHECK_INTERVAL == 5
    
    def test_directory_structure(self):
        """Test that directory structure is correct."""
        assert metadata_dir.parent == chapters_dir
        assert metadata_dir.name == "metadata"
