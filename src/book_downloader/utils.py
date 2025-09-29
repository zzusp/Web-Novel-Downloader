#!/usr/bin/env python3
"""
Utility functions for Novel Downloader.
Contains helper functions for string processing, file operations, and content filtering.
"""

import json
import re
from typing import List, Optional
from pathlib import Path
from .config import chapters_dir


def parse_string_replacements(replacements_str: Optional[str]) -> List[List[str]]:
    """
    Parse string replacements from JSON string.
    Supports both single quotes and double quotes format.
    
    Args:
        replacements_str: JSON string like "[['old1','new1'],['old2','new2']]" or "[['old1','new1'],['old2','new2']]"
        
    Returns:
        List of [old, new] string pairs
    """
    if not replacements_str:
        return []
    
    try:
        # First try parsing as-is
        replacements = json.loads(replacements_str)
    except json.JSONDecodeError:
        try:
            # If that fails, try converting single quotes to double quotes
            # This is a simple approach - replace single quotes with double quotes
            # but we need to be careful about quotes inside strings
            import re
            
            # Convert single quotes to double quotes, but be careful about quotes inside strings
            # This is a simplified approach that works for most cases
            converted_str = replacements_str.replace("'", '"')
            replacements = json.loads(converted_str)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing string replacements: {e}")
            print("Expected format: [['old1','new1'],['old2','new2']] or [[\"old1\",\"new1\"],[\"old2\",\"new2\"]]")
            return []
    
    if not isinstance(replacements, list):
        raise ValueError("String replacements must be a list")
    
    result = []
    for item in replacements:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("Each replacement must be a list with exactly 2 strings")
        if not all(isinstance(s, str) for s in item):
            raise ValueError("Replacement values must be strings")
        result.append(item)
    
    return result


def process_content_with_regex(content: str, content_regex: Optional[str]) -> str:
    """
    Process content with regex filtering.
    
    Args:
        content: Raw content text
        content_regex: Regex pattern to filter content
        
    Returns:
        Processed content text
    """
    if not content_regex:
        return content
        
    try:
        regex_pattern = re.compile(content_regex, re.MULTILINE | re.DOTALL)
        matches = regex_pattern.findall(content)
        if matches:
            # If regex has groups, join them; otherwise use the full matches
            if isinstance(matches[0], tuple):
                # Handle multiple capture groups - join non-empty groups
                clean_matches = []
                for match in matches:
                    joined_match = ''.join(group for group in match if group)
                    if joined_match.strip():
                        clean_matches.append(joined_match.strip())
                processed_content = '\n'.join(clean_matches)
            else:
                # Single capture group or no groups
                clean_matches = [match.strip() for match in matches if match.strip()]
                processed_content = '\n'.join(clean_matches)
            print(f"🔍 Applied regex filter, extracted {len(matches)} matches")
        else:
            print("⚠️  Regex pattern found no matches")
            print(f"   Content preview: {content[:100]}...")
            print(f"   Regex pattern: {content_regex}")
            processed_content = ""
        return processed_content
    except re.error as e:
        print(f"❌ Invalid regex pattern: {e}")
        return content


def apply_string_replacements(content: str, string_replacements: List[List[str]]) -> str:
    """
    Apply string replacements to content.
    
    Args:
        content: Content text to process
        string_replacements: List of [old, new] string pairs
        
    Returns:
        Processed content text
    """
    processed_content = content
    
    for old_str, new_str in string_replacements:
        if old_str in processed_content:
            processed_content = processed_content.replace(old_str, new_str)
            print(f"🔄 Replaced '{old_str}' with '{new_str}'")
    
    return processed_content


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def extract_chapter_title(chapter_file: Path) -> str:
    """Extract chapter title from HTML file's h1 tag."""
    try:
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from lxml import html
        tree = html.fromstring(content)
        title_elems = tree.xpath('//h1')
        
        if len(title_elems) > 0:
            return title_elems[0].text_content().strip()
        else:
            return chapter_file.stem
    except Exception as e:
        print(f"Warning: Could not extract title from {chapter_file.name}: {e}")
        return chapter_file.stem


def sort_chapters_by_metadata(chapter_files: List[Path], metadata_chapters: List[dict], reverse: bool = False) -> List[Path]:
    """
    Sort chapter files based on metadata chapter order.
    
    Args:
        chapter_files: List of chapter file paths
        metadata_chapters: List of chapter metadata from stored JSON
        reverse: Whether to sort in reverse order
        
    Returns:
        Sorted list of chapter files
    """
    # Create a mapping from chapter title to file path
    title_to_file = {}
    for chapter_file in chapter_files:
        # Extract title from filename (remove .html extension)
        filename = chapter_file.stem
        title_to_file[filename] = chapter_file
    
    # Create a mapping from chapter index to file path based on metadata
    index_to_file = {}
    for chapter_info in metadata_chapters:
        title = chapter_info.get("title", "")
        index = chapter_info.get("index", 0)
        
        if title:
            # Try to match with sanitized filename
            safe_title = sanitize_filename(title)
            if safe_title in title_to_file:
                index_to_file[index] = title_to_file[safe_title]
            # Also try original title in case filename wasn't sanitized
            elif title in title_to_file:
                index_to_file[index] = title_to_file[title]
            # Try with spaces replaced by underscores
            elif title.replace(' ', '_') in title_to_file:
                index_to_file[index] = title_to_file[title.replace(' ', '_')]
    
    # Sort by index from metadata
    sorted_indices = sorted(index_to_file.keys(), reverse=reverse)
    sorted_files = [index_to_file[i] for i in sorted_indices]
    
    # Add any unmatched files at the end
    matched_files = set(sorted_files)
    unmatched_files = [f for f in chapter_files if f not in matched_files]
    if unmatched_files:
        print(f"Warning: {len(unmatched_files)} chapter files could not be matched with metadata:")
        for f in unmatched_files:
            print(f"  - {f.name}")
        sorted_files.extend(unmatched_files)
    
    print(f"Sorted {len(sorted_files)} chapters using metadata order ({'reverse' if reverse else 'normal'})")
    return sorted_files
