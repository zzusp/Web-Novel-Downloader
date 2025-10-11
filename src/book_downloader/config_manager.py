#!/usr/bin/env python3
"""
Configuration Manager module for Novel Downloader.
Handles loading, validation, and management of JSON configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .config_validator import ConfigValidator


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self):
        self.validator = ConfigValidator()
        self._config_cache = {}
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load and validate a configuration file.
        
        Args:
            config_path: Path to the JSON configuration file
            
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If configuration validation fails
        """
        config_path = Path(config_path)
        
        # Check if file exists
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Check cache first
        cache_key = str(config_path.absolute())
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # Load JSON file
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in configuration file: {e}")
        
        # Validate configuration
        if not self.validator.validate(config_data):
            raise ValueError(f"Configuration validation failed: {self.validator.get_errors()}")
        
        # Cache the configuration
        self._config_cache[cache_key] = config_data
        
        return config_data
    
    def get_metadata_file_path(self, config_data: Dict[str, Any]) -> str:
        """
        Get the metadata file path based on the hash in configuration.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Path to the metadata file
        """
        hash_value = config_data.get("parsing", {}).get("hash")
        if not hash_value:
            raise ValueError("Missing 'parsing.hash' in configuration")
        
        # Import here to avoid circular imports
        from .config import metadata_dir
        
        return str(metadata_dir / f"chapters_{hash_value}.json")
    
    def get_chapter_dir_path(self, config_data: Dict[str, Any]) -> str:
        """
        Get the chapter directory path based on the hash in configuration.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Path to the chapter directory
        """
        hash_value = config_data.get("parsing", {}).get("hash")
        if not hash_value:
            raise ValueError("Missing 'parsing.hash' in configuration")
        
        # Import here to avoid circular imports
        from .config import chapters_dir
        
        return str(chapters_dir / f"chapters_{hash_value}")
    
    def get_output_file_path(self, config_data: Dict[str, Any]) -> str:
        """
        Get the output file path based on configuration.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            Path to the output file
        """
        output_dir = config_data.get("merging", {}).get("output_directory", "~/Downloads/Novels")
        output_filename = config_data.get("novel", {}).get("output_filename", "novel")
        output_format = config_data.get("merging", {}).get("format", "txt")
        
        # Expand user path
        output_dir = os.path.expanduser(output_dir)
        
        # Create directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        return str(Path(output_dir) / f"{output_filename}.{output_format}")
    
    def validate_chrome_path(self, chrome_path: str) -> bool:
        """
        Validate if Chrome executable exists at the specified path.
        
        Args:
            chrome_path: Path to Chrome executable
            
        Returns:
            True if Chrome executable exists, False otherwise
        """
        if not chrome_path:
            return False
        
        return Path(chrome_path).exists()
    
    def clear_cache(self):
        """Clear the configuration cache."""
        self._config_cache.clear()
