#!/usr/bin/env python3
"""
Task Executor module for Novel Downloader.
Executes complete workflow from configuration file.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .config_manager import ConfigManager


class TaskExecutor:
    """Executes complete novel downloading workflow from configuration."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    async def execute_task(self, config_path: str) -> Dict[str, Any]:
        """
        Execute complete workflow from configuration file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            Dictionary with execution results and statistics
        """
        print(f"[START] Starting task execution with config: {config_path}")
        
        try:
            # Load and validate configuration
            print("[INFO] Loading configuration...")
            config_data = self.config_manager.load_config(config_path)
            print(f"[SUCCESS] Configuration loaded: {config_data.get('task_name', 'Unknown Task')}")
            
            # Get metadata file path
            metadata_file = self.config_manager.get_metadata_file_path(config_data)
            print(f"[INFO] Metadata file: {metadata_file}")
            
            # Execute workflow steps
            results = {
                "config_path": config_path,
                "task_name": config_data.get("task_name", "Unknown Task"),
                "metadata_file": metadata_file,
                "steps": {}
            }
            
            # Step 1: Parse chapters (skip if metadata file already exists)
            print("\n[STEP 1] Parsing chapters...")
            
            # Check if metadata file already exists
            if Path(metadata_file).exists():
                print(f"[INFO] Metadata file already exists: {metadata_file}")
                print("[INFO] Skipping parse step, using existing metadata...")
                
                # Load existing metadata to verify it's valid
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        existing_metadata = json.load(f)
                    
                    # Verify the metadata is for the same URL
                    if existing_metadata.get("menu_url") == config_data["novel"]["menu_url"]:
                        chapters_count = existing_metadata.get("chapter_count", 0)
                        print(f"[SUCCESS] Found existing metadata with {chapters_count} chapters")
                        parse_result = {
                            "success": True, 
                            "metadata_file": metadata_file, 
                            "chapters_count": chapters_count,
                            "skipped": True
                        }
                    else:
                        print("[WARNING] Existing metadata is for different URL, will re-parse...")
                        parse_result = await self._execute_parse_step(config_data, metadata_file)
                except Exception as e:
                    print(f"[WARNING] Error reading existing metadata: {e}")
                    print("[INFO] Will re-parse chapters...")
                    parse_result = await self._execute_parse_step(config_data, metadata_file)
            else:
                print("[INFO] No existing metadata found, parsing chapters...")
                parse_result = await self._execute_parse_step(config_data, metadata_file)
            
            results["steps"]["parse"] = parse_result
            
            if not parse_result["success"]:
                print("[ERROR] Parse step failed, stopping workflow")
                results["success"] = False
                results["error"] = parse_result.get("error", "Parse step failed")
                return results
            
            # Step 2: Download content
            print("\n[STEP 2] Downloading content...")
            download_result = await self._execute_download_step(config_data, metadata_file)
            results["steps"]["download"] = download_result
            
            if not download_result["success"]:
                print("[ERROR] Download step failed, stopping workflow")
                results["success"] = False
                results["error"] = download_result.get("error", "Download step failed")
                return results
            
            # Step 3: Process content (replace)
            print("\n[STEP 3] Processing content...")
            replace_result = await self._execute_replace_step(config_data, metadata_file)
            results["steps"]["replace"] = replace_result
            
            if not replace_result["success"]:
                print("[ERROR] Replace step failed, stopping workflow")
                results["success"] = False
                results["error"] = replace_result.get("error", "Replace step failed")
                return results
            
            # Step 4: Merge files
            print("\n[STEP 4] Merging files...")
            merge_result = await self._execute_merge_step(config_data, metadata_file)
            results["steps"]["merge"] = merge_result
            
            if not merge_result["success"]:
                print("[ERROR] Merge step failed, stopping workflow")
                results["success"] = False
                results["error"] = merge_result.get("error", "Merge step failed")
                return results
            
            # Workflow completed successfully
            print("\n[SUCCESS] Task execution completed successfully!")
            results["success"] = True
            results["output_file"] = merge_result.get("output_file")
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Task execution failed: {e}")
            return {
                "config_path": config_path,
                "success": False,
                "error": str(e),
                "steps": results.get("steps", {})
            }
    
    async def _execute_parse_step(self, config_data: Dict[str, Any], metadata_file: str) -> Dict[str, Any]:
        """Execute parse step."""
        try:
            from .core import NovelDownloader
            
            # Create NovelDownloader instance
            downloader = NovelDownloader(
                chapter_xpath=config_data["parsing"]["chapter_xpath"],
                content_xpath=config_data["parsing"]["content_xpath"],
                concurrency=1,  # Not needed for parsing
                proxy=config_data["browser"].get("proxy"),
                content_regex=config_data["parsing"].get("content_regex"),
                string_replacements=[],  # No string replacements during parsing
                chapter_pagination_xpath=config_data["parsing"].get("chapter_pagination_xpath"),
                chapter_list_pagination_xpath=config_data["parsing"].get("chapter_list_pagination_xpath"),
                headless=config_data["browser"].get("headless", True),
                custom_hash=config_data["parsing"].get("hash"),  # Use the hash from configuration
                chrome_path=config_data["browser"].get("chrome_path")
            )
            
            # Start browser and parse chapters
            await downloader.start_browser()
            chapters = await downloader.parse_chapters(config_data["novel"]["menu_url"])
            await downloader.stop_browser()
            
            if not chapters:
                return {"success": False, "error": "No chapters found"}
            
            # Check if metadata file was created
            if not Path(metadata_file).exists():
                return {"success": False, "error": "Metadata file was not created"}
            
            return {"success": True, "metadata_file": metadata_file, "chapters_count": len(chapters)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_download_step(self, config_data: Dict[str, Any], metadata_file: str) -> Dict[str, Any]:
        """Execute download step."""
        try:
            from .core import NovelDownloader
            
            # Load metadata from file
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Create NovelDownloader instance
            downloader = NovelDownloader(
                chapter_xpath=metadata.get("chapter_xpath"),
                content_xpath=metadata.get("content_xpath"),
                concurrency=config_data["downloading"].get("concurrency", 3),
                proxy=config_data["browser"].get("proxy"),
                content_regex=config_data["downloading"].get("content_regex") or metadata.get("content_regex"),
                string_replacements=metadata.get("string_replacements", []),
                chapter_pagination_xpath=metadata.get("chapter_pagination_xpath"),
                chapter_list_pagination_xpath=metadata.get("chapter_list_pagination_xpath"),
                headless=config_data["browser"].get("headless", True),
                custom_hash=config_data["parsing"].get("hash"),  # Use the hash from configuration
                chrome_path=config_data["browser"].get("chrome_path")
            )
            
            # Start browser and download novel
            await downloader.start_browser()
            stats = await downloader.download_novel(metadata.get("menu_url"))
            await downloader.stop_browser()
            
            return {"success": True, "stats": stats}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_replace_step(self, config_data: Dict[str, Any], metadata_file: str) -> Dict[str, Any]:
        """Execute replace step."""
        try:
            from .cli import replace_chapter_strings
            
            # Get processing configuration
            processing_config = config_data.get("processing", {})
            
            # Execute replace command
            replace_chapter_strings(
                string_replacements=processing_config.get("string_replacements", []),
                regex_replacements=processing_config.get("regex_replacements", []),
                metadata_file=metadata_file,
                case_sensitive=processing_config.get("case_sensitive", False),
                backup=processing_config.get("backup_enabled", False),
                dry_run=False,
                pattern=processing_config.get("file_pattern", "*.html")
            )
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_merge_step(self, config_data: Dict[str, Any], metadata_file: str) -> Dict[str, Any]:
        """Execute merge step."""
        try:
            from .cli import merge_chapters
            
            # Get output file path
            output_file = self.config_manager.get_output_file_path(config_data)
            
            # Execute merge command
            merge_chapters(
                metadata_file=metadata_file,
                output_file=output_file,
                title=config_data["novel"].get("title", "Downloaded Novel"),
                format_type=config_data["merging"].get("format", "txt"),
                author=config_data["novel"].get("author", "Unknown"),
                reverse=config_data["merging"].get("reverse_order", False)
            )
            
            return {"success": True, "output_file": output_file}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
