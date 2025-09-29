"""
Pytest configuration and fixtures for Book Downloader tests.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_browser():
    """Create a mock browser for testing."""
    browser = Mock()
    browser.new_tab.return_value = Mock()
    return browser


@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <head><title>Test Novel</title></head>
        <body>
            <div class="chapter-list">
                <a href="/chapter1" class="chapter-link">Chapter 1</a>
                <a href="/chapter2" class="chapter-link">Chapter 2</a>
                <a href="/chapter3" class="chapter-link">Chapter 3</a>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_chapter_html():
    """Sample chapter HTML content for testing."""
    return """
    <html>
        <head><title>Chapter 1</title></head>
        <body>
            <h1>Chapter 1: The Beginning</h1>
            <div class="content">
                <p>This is the first chapter of the novel.</p>
                <p>It contains some interesting content.</p>
            </div>
        </body>
    </html>
    """
