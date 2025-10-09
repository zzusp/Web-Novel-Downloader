#!/usr/bin/env python3
"""
Metadata management module for Novel Downloader.
Handles chapter metadata storage, loading, and management.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .config import metadata_dir


class MetadataManager:
    """Manages chapter metadata storage and retrieval."""
    
    def __init__(self):
        self.metadata_dir = metadata_dir
    
    def _generate_metadata_filename(self, menu_url: str) -> str:
        """Generate a unique filename for storing chapter metadata."""
        # Create a hash of the URL for consistent filename
        url_hash = hashlib.md5(menu_url.encode('utf-8')).hexdigest()[:8]
        return f"chapters_{url_hash}.json"
    
    def _extract_hash_from_filename(self, filename: str) -> str:
        """Extract hash from metadata filename."""
        # Extract hash from filename like "chapters_879584cc.json"
        if filename.startswith("chapters_") and filename.endswith(".json"):
            return filename[9:-5]  # Remove "chapters_" prefix and ".json" suffix
        return ""
    
    def get_metadata_hash(self, menu_url: str) -> Optional[str]:
        """
        Get the hash for a given menu URL's metadata file.
        
        Args:
            menu_url: URL of the novel's menu page
            
        Returns:
            Hash string if metadata file exists, None otherwise
        """
        filename = self._generate_metadata_filename(menu_url)
        metadata_file = self.metadata_dir / filename
        
        if metadata_file.exists():
            return self._extract_hash_from_filename(filename)
        return None
        
    def save_chapter_metadata(self, menu_url: str, chapters: List[Tuple[str, str]], 
                            chapter_xpath: str, content_xpath: str, 
                            chapter_pagination_xpath: Optional[str] = None,
                            chapter_list_pagination_xpath: Optional[str] = None,
                            content_regex: Optional[str] = None,
                            string_replacements: Optional[List[List[str]]] = None) -> str:
        """
        Save chapter information to a JSON file.
        
        Args:
            menu_url: URL of the novel's menu page
            chapters: List of (chapter_url, chapter_title) tuples
            chapter_xpath: XPath expression used for chapter links
            content_xpath: XPath expression used for chapter content
            chapter_pagination_xpath: Optional XPath expression for chapter pagination links
            chapter_list_pagination_xpath: Optional XPath expression for chapter list pagination links
            content_regex: Optional regex pattern for content filtering
            string_replacements: Optional list of string replacements
            
        Returns:
            Path to the saved metadata file
        """
        metadata = {
            "menu_url": menu_url,
            "timestamp": datetime.now().isoformat(),
            "chapter_xpath": chapter_xpath,
            "content_xpath": content_xpath,
            "chapter_pagination_xpath": chapter_pagination_xpath,
            "chapter_list_pagination_xpath": chapter_list_pagination_xpath,
            "content_regex": content_regex,
            "string_replacements": string_replacements or [],
            "chapter_count": len(chapters),
            "chapters": [
                {"index": i + 1, "url": url, "title": title} 
                for i, (url, title) in enumerate(chapters)
            ]
        }
        
        filename = self._generate_metadata_filename(menu_url)
        metadata_file = self.metadata_dir / filename
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        print(f"Chapter metadata saved to: {metadata_file}")
        return str(metadata_file)
        
    def load_chapter_metadata(self, menu_url: str) -> Optional[Dict[str, Any]]:
        """
        Load chapter information from stored JSON file.
        
        Args:
            menu_url: URL of the novel's menu page
            
        Returns:
            Dictionary with chapter metadata if found, None otherwise
        """
        filename = self._generate_metadata_filename(menu_url)
        metadata_file = self.metadata_dir / filename
        
        if not metadata_file.exists():
            return None
            
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # Verify the metadata is for the same URL
            if metadata.get("menu_url") != menu_url:
                print(f"Warning: Metadata file exists but for different URL")
                print(f"  Expected: {menu_url}")
                print(f"  Found: {metadata.get('menu_url')}")
                return None
                
            return metadata
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Invalid metadata file format: {e}")
            return None
    
    def get_stored_chapters(self, menu_url: str) -> Optional[List[Tuple[str, str, int]]]:
        """
        Get stored chapter information if available.
        
        Args:
            menu_url: URL of the novel's menu page
            
        Returns:
            List of (chapter_url, chapter_title, chapter_index) tuples if found, None otherwise
        """
        metadata = self.load_chapter_metadata(menu_url)
        if metadata is None:
            return None
            
        chapters = []
        for chapter_info in metadata.get("chapters", []):
            chapters.append((chapter_info["url"], chapter_info["title"], chapter_info.get("index", 0)))
            
        return chapters


def find_metadata_files() -> List[Path]:
    """
    Find all metadata JSON files in the metadata directory.
    
    Returns:
        List of metadata file paths
    """
    if not metadata_dir.exists():
        return []
    
    metadata_files = list(metadata_dir.glob("*.json"))
    return metadata_files


def load_metadata_from_file(metadata_file: Path) -> Optional[Dict[str, Any]]:
    """
    Load metadata from a specific JSON file.
    
    Args:
        metadata_file: Path to the metadata JSON file
        
    Returns:
        Dictionary with chapter metadata if valid, None otherwise
    """
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Validate metadata structure
        if not isinstance(metadata, dict):
            return None
            
        if "chapters" not in metadata or not isinstance(metadata["chapters"], list):
            return None
            
        # Check if chapters have required fields
        for chapter in metadata["chapters"]:
            if not isinstance(chapter, dict):
                return None
            if "index" not in chapter or "title" not in chapter or "url" not in chapter:
                return None
                
        return metadata
        
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Warning: Could not load metadata from {metadata_file.name}: {e}")
        return None


def find_best_metadata() -> Optional[Dict[str, Any]]:
    """
    Find the best metadata file to use for merging.
    
    Returns:
        The most recent valid metadata file, or None if none found
    """
    metadata_files = find_metadata_files()
    
    if not metadata_files:
        print("No metadata files found in chapters/metadata/ directory.")
        print("Please run the 'parse' command first to generate chapter metadata.")
        return None
    
    # Try to load each metadata file and find the best one
    valid_metadata = []
    for metadata_file in metadata_files:
        metadata = load_metadata_from_file(metadata_file)
        if metadata:
            # Add file modification time for sorting
            metadata['_file_path'] = metadata_file
            metadata['_file_mtime'] = metadata_file.stat().st_mtime
            valid_metadata.append(metadata)
    
    if not valid_metadata:
        print("No valid metadata files found in chapters/metadata/ directory.")
        print("Please ensure you have run the 'parse' command first.")
        return None
    
    # Sort by modification time (most recent first)
    valid_metadata.sort(key=lambda x: x['_file_mtime'], reverse=True)
    
    best_metadata = valid_metadata[0]
    print(f"Using metadata file: {best_metadata['_file_path'].name}")
    print(f"Found {len(best_metadata['chapters'])} chapters in metadata")
    
    return best_metadata
