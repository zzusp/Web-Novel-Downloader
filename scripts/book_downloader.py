#!/usr/bin/env python3
"""
Book Downloader - Main entry point script.

This script provides the command-line interface for the book downloader tool.
It supports parsing, downloading, merging, and replacing operations for novels.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from book_downloader.cli import main as async_main


def main():
    """Synchronous main function for entry point."""
    import contextlib
    import io
    
    # Create a custom stderr that filters out cleanup errors
    class FilteredStderr:
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            self.cleanup_keywords = [
                'PermissionError', 'WinError 32', 'WinError 145',
                'Extension Rules', 'tempfile.py', 'shutil.py',
                'weakref.py', '_rmtree_unsafe', 'cleanup',
                'OSError', '目录不是空的'
            ]
        
        def write(self, text):
            # Only write to stderr if it's not a cleanup error
            if not any(keyword in text for keyword in self.cleanup_keywords):
                self.original_stderr.write(text)
        
        def flush(self):
            self.original_stderr.flush()
        
        def __getattr__(self, name):
            return getattr(self.original_stderr, name)
    
    # Replace stderr temporarily
    original_stderr = sys.stderr
    sys.stderr = FilteredStderr(original_stderr)
    
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=original_stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=original_stderr)
        sys.exit(1)
    finally:
        # Restore original stderr
        sys.stderr = original_stderr


if __name__ == "__main__":
    main()
