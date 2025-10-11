#!/usr/bin/env python3
"""
Command Line Interface module for Novel Downloader.
Handles command line argument parsing and command execution.
"""

import argparse
import asyncio
import json
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


def merge_chapters(metadata_file: str, output_file: str = "novel.txt", title: str = "Downloaded Novel", 
                  format_type: str = "txt", author: str = "Unknown", reverse: bool = False):
    """
    Merge all downloaded chapters into a single file.
    
    Args:
        metadata_file: Path to the chapters_<hash>.json metadata file
        output_file: Output filename for the merged novel
        title: Title for the novel
        format_type: Output format ('txt' or 'epub')
        author: Author name for epub format
        reverse: Whether to merge in reverse order (default: False for normal order)
    """
    if not chapters_dir.exists():
        print("No chapters directory found. Please download chapters first.")
        return
    
    # Extract hash from metadata file
    metadata_hash = extract_hash_from_metadata_file(metadata_file)
    print(f"Using metadata hash: {metadata_hash}")
    
    chapter_files = find_chapter_files("*.html", metadata_hash)
    if not chapter_files:
        print("No chapter files found. Please download chapters first.")
        return
        
    print(f"Merging {len(chapter_files)} chapters into {output_file}...")
    
    # Load metadata from specified file
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            import json
            metadata = json.load(f)
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Error loading metadata file: {e}")
        return
    
    # Use metadata for chapter ordering
    print(f"Using metadata-based chapter ordering ({'reverse' if reverse else 'normal'} order)...")
    chapter_files = sort_chapters_by_metadata(chapter_files, metadata["chapters"], reverse)
    
    if format_type == "epub":
        create_epub(output_file, title, author, chapter_files, reverse)
    else:
        create_txt(output_file, title, chapter_files)
    
    print(f"Novel merged successfully: {output_file}")


def extract_hash_from_metadata_file(metadata_file_path: str) -> str:
    """
    Extract hash from metadata file path or content.
    
    Args:
        metadata_file_path: Path to the metadata file
        
    Returns:
        Hash string extracted from filename or content
    """
    metadata_path = Path(metadata_file_path)
    
    # If it's a relative path, make it relative to current working directory
    if not metadata_path.is_absolute():
        metadata_path = Path.cwd() / metadata_path
    
    # Extract hash from filename if it matches chapters_<hash>.json pattern
    if metadata_path.name.startswith("chapters_") and metadata_path.name.endswith(".json"):
        return metadata_path.name[9:-5]  # Remove "chapters_" prefix and ".json" suffix
    
    # If filename doesn't match pattern, try to load the file and extract from content
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            import json
            metadata = json.load(f)
            
        # Try to extract hash from menu_url in metadata
        menu_url = metadata.get("menu_url", "")
        if menu_url:
            import hashlib
            url_hash = hashlib.md5(menu_url.encode('utf-8')).hexdigest()[:8]
            return url_hash
            
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Warning: Could not extract hash from metadata file: {e}")
    
    # Fallback: use filename without extension
    return metadata_path.stem


def find_chapter_files(pattern: str = "*.html", metadata_hash: str = None) -> List[Path]:
    """
    Find chapter files in the specified chapters_<hash> subdirectory or all subdirectories.
    
    Args:
        pattern: File pattern to match (default: *.html)
        metadata_hash: Specific hash to search for (if None, searches all subdirectories)
        
    Returns:
        List of chapter file paths
    """
    if not chapters_dir.exists():
        return []
    
    chapter_files = []
    
    if metadata_hash:
        # Search in specific chapters_<hash> subdirectory
        specific_dir = chapters_dir / f"chapters_{metadata_hash}"
        if specific_dir.exists() and specific_dir.is_dir():
            subdir_files = list(specific_dir.glob(pattern))
            chapter_files.extend(subdir_files)
    else:
        # Search for files in all chapters_<hash> subdirectories
        for subdir in chapters_dir.iterdir():
            if subdir.is_dir() and subdir.name.startswith("chapters_"):
                subdir_files = list(subdir.glob(pattern))
                chapter_files.extend(subdir_files)
    
    return chapter_files


def replace_chapter_strings(string_replacements: List[List[str]], 
                           regex_replacements: List[List[str]],
                           metadata_file: str,
                           case_sensitive: bool = False,
                           backup: bool = False,
                           dry_run: bool = False,
                           pattern: str = "*.html"):
    """
    Replace strings in downloaded chapter files.
    
    Args:
        string_replacements: List of [old_string, new_string] pairs
        regex_replacements: List of [pattern, replacement] pairs for regex
        metadata_file: Path to the chapters_<hash>.json metadata file
        case_sensitive: Whether string replacements should be case sensitive
        backup: Whether to create backup files
        dry_run: Whether to preview changes without applying them
        pattern: File pattern to match (default: *.html)
    """
    if not chapters_dir.exists():
        print("No chapters directory found. Please download chapters first.")
        return
    
    # Extract hash from metadata file
    metadata_hash = extract_hash_from_metadata_file(metadata_file)
    print(f"Using metadata hash: {metadata_hash}")
    
    chapter_files = find_chapter_files(pattern, metadata_hash)
    
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
                        # Preserve directory structure in backup
                        relative_path = chapter_file.relative_to(chapters_dir)
                        backup_file = backup_subdir / relative_path
                        backup_file.parent.mkdir(parents=True, exist_ok=True)
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
    parse_parser.add_argument("--chapter-pagination-xpath", 
                                help="Optional XPath expression to extract pagination links within chapters")
    parse_parser.add_argument("--chapter-list-pagination-xpath", 
                                help="Optional XPath expression to extract next page links from chapter list")
    parse_parser.add_argument("--proxy", help="Proxy server to use (e.g., 127.0.0.1:10808)")
    parse_parser.add_argument("--headless", action='store_true', default=True,
                                help="Run browser in headless mode (default: True)")
    parse_parser.add_argument("--no-headless", action='store_false', dest='headless',
                                help="Show browser window (overrides --headless)")
    parse_parser.add_argument("--hash", 
                                help="Custom hash value for metadata file naming (chapters_<hash>.json)")
    
    # Download command - download chapters using stored metadata
    download_parser = subparsers.add_parser('download', help='Download novel chapters using stored metadata')
    download_parser.add_argument("--metadata-file", required=True,
                                help="Path to the chapters_<hash>.json metadata file (supports relative paths)")
    download_parser.add_argument("--content-regex", 
                                help="Optional regex pattern to filter chapter content")
    download_parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                                help=f"Number of concurrent downloads (default: {DEFAULT_CONCURRENCY})")
    download_parser.add_argument("--proxy", help="Proxy server to use (e.g., 127.0.0.1:10808)")
    download_parser.add_argument("--headless", action='store_true', default=True,
                                help="Run browser in headless mode (default: True)")
    download_parser.add_argument("--no-headless", action='store_false', dest='headless',
                                help="Show browser window (overrides --headless)")
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge downloaded chapters')
    merge_parser.add_argument("--metadata-file", required=True,
                                help="Path to the chapters_<hash>.json metadata file (supports relative paths)")
    merge_parser.add_argument("--output", default=DEFAULT_OUTPUT_FILE, help=f"Output filename (default: {DEFAULT_OUTPUT_FILE})")
    merge_parser.add_argument("--title", default=DEFAULT_NOVEL_TITLE, help=f"Novel title (default: {DEFAULT_NOVEL_TITLE})")
    merge_parser.add_argument("--format", choices=['txt', 'epub'], default=DEFAULT_FORMAT, 
                             help=f"Output format: txt or epub (default: {DEFAULT_FORMAT})")
    merge_parser.add_argument("--author", default=DEFAULT_AUTHOR, help=f"Author name for epub (default: {DEFAULT_AUTHOR})")
    merge_parser.add_argument("--reverse", action='store_true', help="Merge chapters in reverse order")
    
    # Replace command - replace strings in downloaded chapters
    replace_parser = subparsers.add_parser('replace', help='Replace strings in downloaded chapter files')
    replace_parser.add_argument("--metadata-file", required=True,
                                help="Path to the chapters_<hash>.json metadata file (supports relative paths)")
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
    
    # Task command - execute complete workflow from configuration file
    task_parser = subparsers.add_parser('task', help='Execute complete workflow from configuration file')
    task_parser.add_argument("--config", required=True,
                            help="Path to the JSON configuration file")
    
    # Config command - configuration management
    config_parser = subparsers.add_parser('config', help='Configuration management commands')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Available config commands')
    
    # Config validate command
    config_validate_parser = config_subparsers.add_parser('validate', help='Validate configuration file')
    config_validate_parser.add_argument("config_file", help="Path to the JSON configuration file to validate")
    
    return parser


async def execute_parse_command(args):
    """Execute the parse command."""
    # Validate custom hash if provided
    if args.hash:
        if not re.match(r'^[a-zA-Z0-9_-]{1,32}$', args.hash):
            print("❌ Error: Hash must be 1-32 characters long and contain only letters, numbers, underscores, and hyphens")
            return
    
    downloader = NovelDownloader(
        chapter_xpath=args.chapter_xpath,
        content_xpath=args.content_xpath,
        concurrency=1,  # Not needed for parsing
        proxy=args.proxy,
        content_regex=args.content_regex,
        string_replacements=[],  # No string replacements during parsing
        chapter_pagination_xpath=args.chapter_pagination_xpath,
        chapter_list_pagination_xpath=args.chapter_list_pagination_xpath,
        headless=args.headless,
        custom_hash=args.hash
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
    """Execute the download command using specified metadata file."""
    # Load metadata from specified file
    try:
        with open(args.metadata_file, 'r', encoding='utf-8') as f:
            import json
            metadata = json.load(f)
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"❌ Error loading metadata file: {e}")
        return
    
    # Extract all parameters from metadata
    menu_url = metadata.get("menu_url")
    chapter_xpath = metadata.get("chapter_xpath")
    content_xpath = metadata.get("content_xpath")
    content_regex = metadata.get("content_regex") or args.content_regex
    string_replacements = metadata.get("string_replacements", [])
    chapter_pagination_xpath = metadata.get("chapter_pagination_xpath")
    chapter_list_pagination_xpath = metadata.get("chapter_list_pagination_xpath")
    
    print(f"📖 Using metadata file: {args.metadata_file}")
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
        chapter_list_pagination_xpath=chapter_list_pagination_xpath,
        headless=args.headless
    )
    
    try:
        await downloader.start_browser()
        stats = await downloader.download_novel(menu_url)
        
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
    merge_chapters(args.metadata_file, args.output, args.title, args.format, args.author, args.reverse)


def execute_replace_command(args):
    """Execute the replace command."""
    string_replacements = parse_string_replacements(args.string_replacements)
    regex_replacements = parse_string_replacements(args.regex_replacements) if args.regex_replacements else []
    replace_chapter_strings(string_replacements, regex_replacements, args.metadata_file,
                           args.case_sensitive, args.backup, args.dry_run, args.pattern)


async def execute_task_command(args):
    """Execute the task command."""
    from .task_executor import TaskExecutor
    
    executor = TaskExecutor()
    result = await executor.execute_task(args.config)
    
    if result["success"]:
        print(f"\n[SUCCESS] Task completed successfully!")
        if "output_file" in result:
            print(f"[OUTPUT] Output file: {result['output_file']}")
    else:
        print(f"\n[ERROR] Task failed: {result.get('error', 'Unknown error')}")
        return 1
    
    return 0


def execute_config_validate_command(args):
    """Execute the config validate command."""
    from .config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    try:
        config_data = config_manager.load_config(args.config_file)
        print(f"[SUCCESS] Configuration file is valid: {args.config_file}")
        print(f"[INFO] Task name: {config_data.get('task_name', 'Unknown')}")
        print(f"[INFO] Novel URL: {config_data.get('novel', {}).get('menu_url', 'Unknown')}")
        return 0
    except FileNotFoundError:
        print(f"[ERROR] Configuration file not found: {args.config_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in configuration file: {e}")
        return 1
    except ValueError as e:
        print(f"[ERROR] Configuration validation failed: {e}")
        return 1


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
    elif args.command == 'task':
        return await execute_task_command(args)
    elif args.command == 'config':
        if args.config_command == 'validate':
            return execute_config_validate_command(args)
        else:
            parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1
    
    return 0
