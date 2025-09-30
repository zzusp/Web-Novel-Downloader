#!/usr/bin/env python3
"""
Command Line Interface module for Novel Downloader.
Handles command line argument parsing and command execution.
"""

import argparse
import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import List

from .config import chapters_dir, DEFAULT_CONCURRENCY, DEFAULT_OUTPUT_FILE, DEFAULT_NOVEL_TITLE, DEFAULT_AUTHOR, DEFAULT_FORMAT, DEFAULT_FILE_PATTERN
from .core import NovelDownloader
from .utils import parse_string_replacements, sort_chapters_by_metadata
from .metadata import find_best_metadata
from .epub_generator import create_epub


def create_txt(output_file: str, title: str, chapter_files: List[Path]):
    """Create a plain text file from chapters."""
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f"{title}\n")
        outfile.write("=" * len(title) + "\n\n")
        
        for chapter_file in chapter_files:
            print(f"Adding: {chapter_file.name}")
            with open(chapter_file, 'r', encoding='utf-8') as infile:
                content = infile.read()
                # Extract text content, removing HTML tags
                from lxml import html
                tree = html.fromstring(content)
                text_content = tree.text_content()
                outfile.write(text_content + "\n\n")


def merge_chapters(output_file: str = "novel.txt", title: str = "Downloaded Novel", 
                  format_type: str = "txt", author: str = "Unknown", reverse: bool = False):
    """
    Merge all downloaded chapters into a single file.
    
    Args:
        output_file: Output filename for the merged novel
        title: Title for the novel
        format_type: Output format ('txt' or 'epub')
        author: Author name for epub format
        reverse: Whether to merge in reverse order (default: False for normal order)
    """
    if not chapters_dir.exists():
        print("No chapters directory found. Please download chapters first.")
        return
        
    chapter_files = list(chapters_dir.glob("*.html"))
    if not chapter_files:
        print("No chapter files found. Please download chapters first.")
        return
        
    print(f"Merging {len(chapter_files)} chapters into {output_file}...")
    
    # Find and load metadata from chapters/metadata/ directory
    metadata = find_best_metadata()
    if not metadata:
        return
    
    # Use metadata for chapter ordering
    print(f"Using metadata-based chapter ordering ({'reverse' if reverse else 'normal'} order)...")
    chapter_files = sort_chapters_by_metadata(chapter_files, metadata["chapters"], reverse)
    
    if format_type == "epub":
        create_epub(output_file, title, author, chapter_files, reverse)
    else:
        create_txt(output_file, title, chapter_files)
    
    print(f"Novel merged successfully: {output_file}")


def replace_chapter_strings(string_replacements: List[List[str]], 
                           regex_replacements: List[List[str]],
                           case_sensitive: bool = False,
                           backup: bool = False,
                           dry_run: bool = False,
                           pattern: str = "*.html"):
    """
    Replace strings in downloaded chapter files.
    
    Args:
        string_replacements: List of [old_string, new_string] pairs
        regex_replacements: List of [pattern, replacement] pairs for regex
        case_sensitive: Whether string replacements should be case sensitive
        backup: Whether to create backup files
        dry_run: Whether to preview changes without applying them
        pattern: File pattern to match (default: *.html)
    """
    if not chapters_dir.exists():
        print("No chapters directory found. Please download chapters first.")
        return
        
    chapter_files = list(chapters_dir.glob(pattern))
    
    if not chapter_files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(chapter_files)} files to process")
    
    if dry_run:
        print("🔍 DRY RUN MODE - Previewing changes without applying them")
    
    if backup and not dry_run:
        print("📁 Creating backup files...")
        backup_dir = chapters_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = backup_dir / f"backup_{timestamp}"
        backup_subdir.mkdir(exist_ok=True)
    
    processed_count = 0
    modified_count = 0
    
    for chapter_file in chapter_files:
        try:
            print(f"Processing: {chapter_file.name}")
            
            # Read file content
            with open(chapter_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            file_modified = False
            
            # Apply string replacements
            for old_str, new_str in string_replacements:
                if case_sensitive:
                    if old_str in content:
                        content = content.replace(old_str, new_str)
                        file_modified = True
                        print(f"  String replacement: '{old_str}' -> '{new_str}'")
                else:
                    # Case insensitive replacement
                    pattern = re.escape(old_str)
                    if re.search(pattern, content, re.IGNORECASE):
                        content = re.sub(pattern, new_str, content, flags=re.IGNORECASE)
                        file_modified = True
                        print(f"  String replacement (case insensitive): '{old_str}' -> '{new_str}'")
            
            # Apply regex replacements
            for pattern, replacement in regex_replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    file_modified = True
                    print(f"  Regex replacement: '{pattern}' -> '{replacement}'")
            
            if file_modified:
                modified_count += 1
                
                if dry_run:
                    print(f"  📝 Would modify: {chapter_file.name}")
                    # Show a preview of changes
                    if len(content) != len(original_content):
                        print(f"    Content length changed: {len(original_content)} -> {len(content)}")
                else:
                    # Create backup if requested
                    if backup:
                        backup_file = backup_subdir / chapter_file.name
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            f.write(original_content)
                        print(f"  💾 Backup created: {backup_file}")
                    
                    # Write modified content
                    with open(chapter_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✅ Modified: {chapter_file.name}")
            else:
                print(f"  ⏭️  No changes needed: {chapter_file.name}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {chapter_file.name}: {e}")
            continue
    
    print(f"\n📊 Summary:")
    print(f"  Processed: {processed_count} files")
    print(f"  Modified: {modified_count} files")
    
    if dry_run:
        print("🔍 This was a dry run - no files were actually modified")
    elif backup and modified_count > 0:
        print(f"💾 Backup files saved to: {backup_subdir}")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(description="Novel Downloader with configurable XPath expressions")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command - extract and store chapter information
    parse_parser = subparsers.add_parser('parse', help='Parse and store chapter information from URL')
    parse_parser.add_argument("menu_url", help="URL of the novel's menu/chapter list page")
    parse_parser.add_argument("--chapter-xpath", required=True, 
                                help="XPath expression to extract chapter links (should match <a> tags)")
    parse_parser.add_argument("--content-xpath", required=True,
                                help="XPath expression to extract chapter content")
    parse_parser.add_argument("--content-regex", 
                                help="Optional regex pattern to filter chapter content")
    parse_parser.add_argument("--string-replacements", 
                                help="JSON string of string replacements: [['old1','new1'],['old2','new2']]")
    parse_parser.add_argument("--chapter-pagination-xpath", 
                                help="Optional XPath expression to extract pagination links within chapters")
    parse_parser.add_argument("--chapter-list-pagination-xpath", 
                                help="Optional XPath expression to extract next page links from chapter list")
    parse_parser.add_argument("--proxy", help="Proxy server to use (e.g., 127.0.0.1:10808)")
    
    # Download command - download chapters using stored metadata
    download_parser = subparsers.add_parser('download', help='Download novel chapters using stored metadata')
    download_parser.add_argument("--content-regex", 
                                help="Optional regex pattern to filter chapter content")
    download_parser.add_argument("--string-replacements", 
                                help="JSON string of string replacements: [['old1','new1'],['old2','new2']]")
    download_parser.add_argument("--chapter-pagination-xpath", 
                                help="Optional XPath expression to extract pagination links within chapters")
    download_parser.add_argument("--chapter-list-pagination-xpath", 
                                help="Optional XPath expression to extract next page links from chapter list")
    download_parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                                help=f"Number of concurrent downloads (default: {DEFAULT_CONCURRENCY})")
    download_parser.add_argument("--proxy", help="Proxy server to use (e.g., 127.0.0.1:10808)")
    download_parser.add_argument("--force-parse", action='store_true',
                                help="Force parsing from URL even if stored data exists")
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge downloaded chapters')
    merge_parser.add_argument("--output", default=DEFAULT_OUTPUT_FILE, help=f"Output filename (default: {DEFAULT_OUTPUT_FILE})")
    merge_parser.add_argument("--title", default=DEFAULT_NOVEL_TITLE, help=f"Novel title (default: {DEFAULT_NOVEL_TITLE})")
    merge_parser.add_argument("--format", choices=['txt', 'epub'], default=DEFAULT_FORMAT, 
                             help=f"Output format: txt or epub (default: {DEFAULT_FORMAT})")
    merge_parser.add_argument("--author", default=DEFAULT_AUTHOR, help=f"Author name for epub (default: {DEFAULT_AUTHOR})")
    merge_parser.add_argument("--reverse", action='store_true', help="Merge chapters in reverse order")
    
    # Replace command - replace strings in downloaded chapters
    replace_parser = subparsers.add_parser('replace', help='Replace strings in downloaded chapter files')
    replace_parser.add_argument("--string-replacements", required=True,
                                help="JSON string of string replacements: [['old1','new1'],['old2','new2']]")
    replace_parser.add_argument("--regex-replacements", 
                                help="JSON string of regex replacements: [['pattern1','replacement1'],['pattern2','replacement2']]")
    replace_parser.add_argument("--case-sensitive", action='store_true',
                                help="Make string replacements case sensitive (default: case insensitive)")
    replace_parser.add_argument("--backup", action='store_true',
                                help="Create backup files before replacement")
    replace_parser.add_argument("--dry-run", action='store_true',
                                help="Preview changes without actually replacing")
    replace_parser.add_argument("--pattern", default=DEFAULT_FILE_PATTERN,
                                help=f"File pattern to match (default: {DEFAULT_FILE_PATTERN})")
    
    return parser


async def execute_parse_command(args):
    """Execute the parse command."""
    string_replacements = parse_string_replacements(args.string_replacements)
    downloader = NovelDownloader(
        chapter_xpath=args.chapter_xpath,
        content_xpath=args.content_xpath,
        concurrency=1,  # Not needed for parsing
        proxy=args.proxy,
        content_regex=args.content_regex,
        string_replacements=string_replacements,
        chapter_pagination_xpath=args.chapter_pagination_xpath,
        chapter_list_pagination_xpath=args.chapter_list_pagination_xpath
    )
    
    try:
        await downloader.start_browser()
        chapters = await downloader.parse_chapters(args.menu_url)
        
        if chapters:
            print(f"\nParse Summary:")
            print(f"Total chapters found: {len(chapters)}")
            print("Chapter information has been saved for future downloads.")
        else:
            print("No chapters found. Please check your XPath expressions.")
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await downloader.stop_browser()
        except Exception as e:
            print(f"Warning: Error stopping browser: {e}")
        
        # Suppress internal cleanup exceptions that are not user-friendly
        import sys
        import io
        from contextlib import redirect_stderr
        
        with redirect_stderr(io.StringIO()):
            # Force cleanup
            import gc
            gc.collect()


async def execute_download_command(args):
    """Execute the download command using stored metadata."""
    # Load metadata - this is required for download command
    metadata = find_best_metadata()
    if not metadata:
        print("❌ Error: No metadata found.")
        print("Please run 'parse' command first to generate chapter metadata.")
        return
    
    # Extract all parameters from metadata
    menu_url = metadata.get("menu_url")
    chapter_xpath = metadata.get("chapter_xpath")
    content_xpath = metadata.get("content_xpath")
    content_regex = metadata.get("content_regex") or args.content_regex
    string_replacements = parse_string_replacements(args.string_replacements) or metadata.get("string_replacements", [])
    chapter_pagination_xpath = metadata.get("chapter_pagination_xpath") or args.chapter_pagination_xpath
    chapter_list_pagination_xpath = metadata.get("chapter_list_pagination_xpath") or args.chapter_list_pagination_xpath
    
    print(f"📖 Using metadata: {metadata['_file_path'].name}")
    print(f"📖 Menu URL: {menu_url}")
    print(f"📖 Chapter XPath: {chapter_xpath}")
    print(f"📖 Content XPath: {content_xpath}")
    if content_regex:
        print(f"📖 Content Regex: {content_regex}")
    if string_replacements:
        print(f"📖 String Replacements: {len(string_replacements)} rules")
    if chapter_pagination_xpath:
        print(f"📖 Chapter Pagination XPath: {chapter_pagination_xpath}")
    if chapter_list_pagination_xpath:
        print(f"📖 Chapter List Pagination XPath: {chapter_list_pagination_xpath}")
    
    downloader = NovelDownloader(
        chapter_xpath=chapter_xpath,
        content_xpath=content_xpath,
        concurrency=args.concurrency,
        proxy=args.proxy,
        content_regex=content_regex,
        string_replacements=string_replacements,
        chapter_pagination_xpath=chapter_pagination_xpath,
        chapter_list_pagination_xpath=chapter_list_pagination_xpath
    )
    
    try:
        await downloader.start_browser()
        stats = await downloader.download_novel(menu_url, force_parse=args.force_parse)
        
        print("\n📊 Download Summary:")
        print(f"Total chapters: {stats['total']}")
        print(f"Downloaded: {stats['downloaded']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"Failed: {stats['failed']}")
        
        if 'error' in stats:
            print(f"❌ Error: {stats['error']}")
        
    except Exception as e:
        print(f"❌ Error during download: {e}")
        print("\n💡 故障排除建议:")
        print("   1. 检查网站是否可以在浏览器中正常访问")
        print("   2. 确认代理设置是否正确 (如果使用代理)")
        print("   3. 尝试重新运行 'parse' 命令刷新章节链接")
        print("   4. 检查小说URL是否已更改")
        print("   5. 确认网络连接是否正常")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await downloader.stop_browser()
        except Exception as e:
            print(f"Warning: Error stopping browser: {e}")
        
        # Suppress internal cleanup exceptions that are not user-friendly
        import sys
        import io
        from contextlib import redirect_stderr
        
        with redirect_stderr(io.StringIO()):
            # Force cleanup
            import gc
            gc.collect()


def execute_merge_command(args):
    """Execute the merge command."""
    merge_chapters(args.output, args.title, args.format, args.author, args.reverse)


def execute_replace_command(args):
    """Execute the replace command."""
    string_replacements = parse_string_replacements(args.string_replacements)
    regex_replacements = parse_string_replacements(args.regex_replacements) if args.regex_replacements else []
    replace_chapter_strings(string_replacements, regex_replacements, 
                           args.case_sensitive, args.backup, args.dry_run, args.pattern)


async def main():
    """Main function to handle command line arguments and execute commands."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    if args.command == 'parse':
        await execute_parse_command(args)
    elif args.command == 'download':
        await execute_download_command(args)
    elif args.command == 'merge':
        execute_merge_command(args)
    elif args.command == 'replace':
        execute_replace_command(args)
    else:
        parser.print_help()
