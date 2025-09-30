import argparse
import asyncio
import os
import sys
import tempfile
from lxml import html
from pydoll.browser import Chrome

# Set environment variables to reduce temp file issues on Windows
temp_dir = os.path.join(os.getcwd(), 'temp')
os.makedirs(temp_dir, exist_ok=True)
os.environ['PYDOLL_TEMP_DIR'] = temp_dir

async def main():
    parser = argparse.ArgumentParser(description="Scrape a webpage.")
    parser.add_argument("url", help="The URL to scrape.")
    parser.add_argument("--proxy", help="The proxy to use (e.g., 127.0.0.1:10808).")
    parser.add_argument("--xpath", help="The XPath expression to use.", default="//body")
    args = parser.parse_args()

    # Create Chrome browser instance
    browser = Chrome()
    await browser.start()
    
    try:
        # Create a new tab and navigate to the URL
        tab = await browser.new_tab()
        await tab.go_to(args.url)
        
        # Get the page HTML
        html_content = await tab.page_source
        
        # Parse with lxml and apply XPath
        tree = html.fromstring(html_content)
        result = tree.xpath(args.xpath)
        
        if isinstance(result, list):
            for item in result:
                print(item)
        else:
            print(result)
            
    finally:
        try:
            await browser.stop()
        except (PermissionError, OSError, FileNotFoundError) as e:
            # Ignore cleanup errors on Windows - they don't affect functionality
            # These are typically temporary file cleanup issues
            pass
        
        # Suppress internal cleanup exceptions that are not user-friendly
        import sys
        import io
        from contextlib import redirect_stderr
        
        with redirect_stderr(io.StringIO()):
            # Force cleanup
            import gc
            gc.collect()

if __name__ == "__main__":
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
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=original_stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=original_stderr)
        sys.exit(1)
    finally:
        # Restore original stderr
        sys.stderr = original_stderr
