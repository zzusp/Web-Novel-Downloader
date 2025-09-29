#!/usr/bin/env python3
"""
Configuration module for Novel Downloader.
Contains constants, directory setup, and environment configuration.
"""

import os
from pathlib import Path

# Set environment variables to reduce temp file issues on Windows
temp_dir = os.path.join(os.getcwd(), 'temp')
os.makedirs(temp_dir, exist_ok=True)
os.environ['PYDOLL_TEMP_DIR'] = temp_dir

# Create chapters directory
chapters_dir = Path('chapters')
chapters_dir.mkdir(exist_ok=True)

# Create metadata directory for chapter information storage
metadata_dir = Path('chapters/metadata')
metadata_dir.mkdir(exist_ok=True)

# Default configuration values
DEFAULT_CONCURRENCY = 3
DEFAULT_OUTPUT_FILE = "novel.txt"
DEFAULT_NOVEL_TITLE = "Downloaded Novel"
DEFAULT_AUTHOR = "Unknown"
DEFAULT_FORMAT = "txt"

# Cloudflare protection settings
CLOUDFLARE_MAX_WAIT_TIME = 120  # Maximum wait time in seconds (2 minutes)
CLOUDFLARE_CHECK_INTERVAL = 3   # Check every 3 seconds

# File patterns
DEFAULT_FILE_PATTERN = "*.html"
