#!/usr/bin/env python3
"""
Configuration Validator module for Novel Downloader.
Validates JSON configuration files against schema and business rules.
"""

import re
from typing import Dict, Any, List, Optional


class ConfigValidator:
    """Validates configuration data structure and content."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, config_data: Dict[str, Any]) -> bool:
        """
        Validate configuration data.
        
        Args:
            config_data: Configuration data dictionary
            
        Returns:
            True if validation passes, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        # Validate top-level structure
        if not self._validate_top_level(config_data):
            return False
        
        # Validate browser section
        if not self._validate_browser(config_data.get("browser", {})):
            return False
        
        # Validate novel section
        if not self._validate_novel(config_data.get("novel", {})):
            return False
        
        # Validate parsing section
        if not self._validate_parsing(config_data.get("parsing", {})):
            return False
        
        # Validate downloading section
        if not self._validate_downloading(config_data.get("downloading", {})):
            return False
        
        # Validate processing section
        if not self._validate_processing(config_data.get("processing", {})):
            return False
        
        # Validate merging section
        if not self._validate_merging(config_data.get("merging", {})):
            return False
        
        return len(self.errors) == 0
    
    def _validate_top_level(self, config_data: Dict[str, Any]) -> bool:
        """Validate top-level configuration structure."""
        required_fields = ["version", "task_name", "description"]
        
        for field in required_fields:
            if field not in config_data:
                self.errors.append(f"Missing required field: {field}")
                return False
        
        # Validate version
        if not isinstance(config_data["version"], str):
            self.errors.append("Field 'version' must be a string")
            return False
        
        # Validate task_name
        if not isinstance(config_data["task_name"], str) or not config_data["task_name"].strip():
            self.errors.append("Field 'task_name' must be a non-empty string")
            return False
        
        # Validate description
        if not isinstance(config_data["description"], str):
            self.errors.append("Field 'description' must be a string")
            return False
        
        return True
    
    def _validate_browser(self, browser_config: Dict[str, Any]) -> bool:
        """Validate browser configuration section."""
        if not browser_config:
            self.errors.append("Missing required section: 'browser'")
            return False
        
        # Validate chrome_path
        chrome_path = browser_config.get("chrome_path")
        if not chrome_path or not isinstance(chrome_path, str):
            self.errors.append("Field 'browser.chrome_path' is required and must be a string")
            return False
        
        # Validate headless
        if "headless" in browser_config and not isinstance(browser_config["headless"], bool):
            self.errors.append("Field 'browser.headless' must be a boolean")
            return False
        
        # Validate proxy
        if "proxy" in browser_config and browser_config["proxy"] is not None:
            if not isinstance(browser_config["proxy"], str):
                self.errors.append("Field 'browser.proxy' must be a string or null")
                return False
        
        return True
    
    def _validate_novel(self, novel_config: Dict[str, Any]) -> bool:
        """Validate novel configuration section."""
        if not novel_config:
            self.errors.append("Missing required section: 'novel'")
            return False
        
        # Validate menu_url
        menu_url = novel_config.get("menu_url")
        if not menu_url or not isinstance(menu_url, str):
            self.errors.append("Field 'novel.menu_url' is required and must be a string")
            return False
        
        # Validate URL format
        if not self._is_valid_url(menu_url):
            self.errors.append("Field 'novel.menu_url' must be a valid URL")
            return False
        
        # Validate title
        if "title" in novel_config and not isinstance(novel_config["title"], str):
            self.errors.append("Field 'novel.title' must be a string")
            return False
        
        # Validate author
        if "author" in novel_config and not isinstance(novel_config["author"], str):
            self.errors.append("Field 'novel.author' must be a string")
            return False
        
        # Validate output_filename
        if "output_filename" in novel_config and not isinstance(novel_config["output_filename"], str):
            self.errors.append("Field 'novel.output_filename' must be a string")
            return False
        
        return True
    
    def _validate_parsing(self, parsing_config: Dict[str, Any]) -> bool:
        """Validate parsing configuration section."""
        if not parsing_config:
            self.errors.append("Missing required section: 'parsing'")
            return False
        
        # Validate hash
        hash_value = parsing_config.get("hash")
        if not hash_value or not isinstance(hash_value, str):
            self.errors.append("Field 'parsing.hash' is required and must be a string")
            return False
        
        # Validate hash format (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', hash_value):
            self.errors.append("Field 'parsing.hash' must contain only alphanumeric characters and underscores")
            return False
        
        # Validate chapter_xpath
        chapter_xpath = parsing_config.get("chapter_xpath")
        if not chapter_xpath or not isinstance(chapter_xpath, str):
            self.errors.append("Field 'parsing.chapter_xpath' is required and must be a string")
            return False
        
        # Validate content_xpath
        content_xpath = parsing_config.get("content_xpath")
        if not content_xpath or not isinstance(content_xpath, str):
            self.errors.append("Field 'parsing.content_xpath' is required and must be a string")
            return False
        
        # Validate optional fields
        optional_fields = ["chapter_pagination_xpath", "chapter_list_pagination_xpath", "content_regex"]
        for field in optional_fields:
            if field in parsing_config and parsing_config[field] is not None:
                if not isinstance(parsing_config[field], str):
                    self.errors.append(f"Field 'parsing.{field}' must be a string or null")
                    return False
        
        return True
    
    def _validate_downloading(self, downloading_config: Dict[str, Any]) -> bool:
        """Validate downloading configuration section."""
        if not downloading_config:
            self.errors.append("Missing required section: 'downloading'")
            return False
        
        # Validate concurrency
        concurrency = downloading_config.get("concurrency")
        if concurrency is not None:
            if not isinstance(concurrency, int) or concurrency < 1:
                self.errors.append("Field 'downloading.concurrency' must be a positive integer")
                return False
        
        # Validate content_regex
        if "content_regex" in downloading_config and downloading_config["content_regex"] is not None:
            if not isinstance(downloading_config["content_regex"], str):
                self.errors.append("Field 'downloading.content_regex' must be a string or null")
                return False
        
        return True
    
    def _validate_processing(self, processing_config: Dict[str, Any]) -> bool:
        """Validate processing configuration section."""
        if not processing_config:
            self.errors.append("Missing required section: 'processing'")
            return False
        
        # Validate string_replacements
        string_replacements = processing_config.get("string_replacements", [])
        if not isinstance(string_replacements, list):
            self.errors.append("Field 'processing.string_replacements' must be a list")
            return False
        
        for i, replacement in enumerate(string_replacements):
            if not isinstance(replacement, list) or len(replacement) != 2:
                self.errors.append(f"Field 'processing.string_replacements[{i}]' must be a list with exactly 2 elements")
                return False
            if not all(isinstance(item, str) for item in replacement):
                self.errors.append(f"Field 'processing.string_replacements[{i}]' must contain only strings")
                return False
        
        # Validate regex_replacements
        regex_replacements = processing_config.get("regex_replacements", [])
        if not isinstance(regex_replacements, list):
            self.errors.append("Field 'processing.regex_replacements' must be a list")
            return False
        
        for i, replacement in enumerate(regex_replacements):
            if not isinstance(replacement, list) or len(replacement) != 2:
                self.errors.append(f"Field 'processing.regex_replacements[{i}]' must be a list with exactly 2 elements")
                return False
            if not all(isinstance(item, str) for item in replacement):
                self.errors.append(f"Field 'processing.regex_replacements[{i}]' must contain only strings")
                return False
        
        # Validate case_sensitive
        if "case_sensitive" in processing_config and not isinstance(processing_config["case_sensitive"], bool):
            self.errors.append("Field 'processing.case_sensitive' must be a boolean")
            return False
        
        # Validate backup_enabled
        if "backup_enabled" in processing_config and not isinstance(processing_config["backup_enabled"], bool):
            self.errors.append("Field 'processing.backup_enabled' must be a boolean")
            return False
        
        # Validate file_pattern
        if "file_pattern" in processing_config and not isinstance(processing_config["file_pattern"], str):
            self.errors.append("Field 'processing.file_pattern' must be a string")
            return False
        
        return True
    
    def _validate_merging(self, merging_config: Dict[str, Any]) -> bool:
        """Validate merging configuration section."""
        if not merging_config:
            self.errors.append("Missing required section: 'merging'")
            return False
        
        # Validate format
        format_value = merging_config.get("format", "txt")
        if format_value not in ["txt", "epub"]:
            self.errors.append("Field 'merging.format' must be either 'txt' or 'epub'")
            return False
        
        # Validate reverse_order
        if "reverse_order" in merging_config and not isinstance(merging_config["reverse_order"], bool):
            self.errors.append("Field 'merging.reverse_order' must be a boolean")
            return False
        
        # Validate output_directory
        if "output_directory" in merging_config and not isinstance(merging_config["output_directory"], str):
            self.errors.append("Field 'merging.output_directory' must be a string")
            return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()
    
    def get_warnings(self) -> List[str]:
        """Get validation warnings."""
        return self.warnings.copy()
    
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return len(self.warnings) > 0
