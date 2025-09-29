"""
Tests for utility functions.
"""

import pytest
from book_downloader.utils import (
    parse_string_replacements,
    process_content_with_regex,
    apply_string_replacements,
    sanitize_filename,
    extract_chapter_title,
)
from pathlib import Path


class TestParseStringReplacements:
    """Test string replacement parsing."""
    
    def test_parse_double_quotes(self):
        """Test parsing with double quotes."""
        result = parse_string_replacements('[["old1","new1"],["old2","new2"]]')
        assert result == [["old1", "new1"], ["old2", "new2"]]
    
    def test_parse_single_quotes(self):
        """Test parsing with single quotes."""
        result = parse_string_replacements("[['old1','new1'],['old2','new2']]")
        assert result == [["old1", "new1"], ["old2", "new2"]]
    
    def test_parse_empty(self):
        """Test parsing empty string."""
        result = parse_string_replacements("")
        assert result == []
    
    def test_parse_none(self):
        """Test parsing None."""
        result = parse_string_replacements(None)
        assert result == []


class TestProcessContentWithRegex:
    """Test regex content processing."""
    
    def test_no_regex(self):
        """Test with no regex pattern."""
        content = "Some content"
        result = process_content_with_regex(content, None)
        assert result == content
    
    def test_simple_regex(self):
        """Test with simple regex pattern."""
        content = "Chapter 1: The Beginning\nSome text\nChapter 2: The End"
        result = process_content_with_regex(content, r"Chapter \d+: .*")
        assert "Chapter 1: The Beginning" in result
        assert "Chapter 2: The End" in result


class TestApplyStringReplacements:
    """Test string replacement application."""
    
    def test_no_replacements(self):
        """Test with no replacements."""
        content = "Some content"
        result = apply_string_replacements(content, [])
        assert result == content
    
    def test_single_replacement(self):
        """Test with single replacement."""
        content = "Hello world"
        result = apply_string_replacements(content, [["world", "universe"]])
        assert result == "Hello universe"
    
    def test_multiple_replacements(self):
        """Test with multiple replacements."""
        content = "Hello world, this is a test"
        result = apply_string_replacements(content, [["world", "universe"], ["test", "example"]])
        assert result == "Hello universe, this is a example"


class TestSanitizeFilename:
    """Test filename sanitization."""
    
    def test_safe_filename(self):
        """Test with safe filename."""
        result = sanitize_filename("chapter1")
        assert result == "chapter1"
    
    def test_unsafe_filename(self):
        """Test with unsafe filename."""
        result = sanitize_filename("chapter<1>: test")
        assert result == "chapter_1___ test"
    
    def test_empty_filename(self):
        """Test with empty filename."""
        result = sanitize_filename("")
        assert result == ""


class TestExtractChapterTitle:
    """Test chapter title extraction."""
    
    def test_extract_from_html(self, temp_dir, sample_chapter_html):
        """Test extracting title from HTML file."""
        chapter_file = temp_dir / "test.html"
        chapter_file.write_text(sample_chapter_html)
        
        result = extract_chapter_title(chapter_file)
        assert result == "Chapter 1: The Beginning"
    
    def test_extract_fallback(self, temp_dir):
        """Test fallback to filename when no h1 tag."""
        chapter_file = temp_dir / "test.html"
        chapter_file.write_text("<html><body><p>No title here</p></body></html>")
        
        result = extract_chapter_title(chapter_file)
        assert result == "test"  # filename without extension
