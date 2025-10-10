#!/usr/bin/env python3
"""
Core module for Novel Downloader.
Contains the main NovelDownloader class and related functionality.
"""

import asyncio
import re
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, cast
from urllib.parse import urljoin
from lxml import html
from pydoll.browser import Chrome
from pydoll.constants import By
from pydoll.elements.web_element import WebElement

from .config import chapters_dir, CLOUDFLARE_MAX_WAIT_TIME, CLOUDFLARE_CHECK_INTERVAL
from .utils import process_content_with_regex, apply_string_replacements, sanitize_filename
from .metadata import MetadataManager


class NovelDownloader:
    """Main class for downloading novels with configurable XPath expressions."""
    
    def __init__(self, 
                 chapter_xpath: str,
                 content_xpath: str,
                 concurrency: int = 3,
                 proxy: Optional[str] = None,
                 content_regex: Optional[str] = None,
                 string_replacements: Optional[List[List[str]]] = None,
                 chapter_pagination_xpath: Optional[str] = None,
                 chapter_list_pagination_xpath: Optional[str] = None):
        """
        Initialize the novel downloader.
        
        Args:
            chapter_xpath: XPath expression to extract chapter links
            content_xpath: XPath expression to extract chapter content
            concurrency: Number of concurrent downloads (default: 3)
            proxy: Proxy server to use (optional)
            content_regex: Optional regex pattern to filter chapter content
            string_replacements: Optional list of [old, new] string pairs for replacement
            chapter_pagination_xpath: Optional XPath expression to extract pagination links within chapters
            chapter_list_pagination_xpath: Optional XPath expression to extract next page links from chapter list
        """
        self.chapter_xpath = chapter_xpath
        self.content_xpath = content_xpath
        self.concurrency = concurrency
        self.proxy = proxy
        self.content_regex = content_regex
        self.string_replacements = string_replacements or []
        self.chapter_pagination_xpath = chapter_pagination_xpath
        self.chapter_list_pagination_xpath = chapter_list_pagination_xpath
        self.browser = None
        self.semaphore = asyncio.Semaphore(concurrency)
        self.metadata_manager = MetadataManager()
        
    def _process_content(self, content: str) -> str:
        """
        Process chapter content with regex filtering and string replacements.
        
        Args:
            content: Raw content text from XPath extraction
            
        Returns:
            Processed content text
        """
        processed_content = content
        
        # Apply regex filtering if specified
        if self.content_regex:
            processed_content = process_content_with_regex(processed_content, self.content_regex)
        
        # Apply string replacements
        if self.string_replacements:
            processed_content = apply_string_replacements(processed_content, self.string_replacements)
        
        return processed_content
        
    async def start_browser(self):
        """Start the browser instance."""
        self.browser = Chrome()
        await self.browser.start()
        
    async def stop_browser(self):
        """Stop the browser instance."""
        if self.browser:
            try:
                await self.browser.stop()
                # Wait a bit for cleanup
                await asyncio.sleep(3)
            except (PermissionError, OSError, FileNotFoundError, Exception) as e:
                # Ignore cleanup errors on Windows - these are typically temporary file cleanup issues
                # that don't affect functionality. Only show warning for non-permission errors.
                if not isinstance(e, PermissionError):
                    print(f"Warning: Browser cleanup warning (can be ignored): {e}")
                pass
            finally:
                self.browser = None
                # Suppress internal cleanup exceptions that are not user-friendly
                import sys
                import io
                from contextlib import redirect_stderr
                
                # Redirect stderr to suppress cleanup exceptions
                with redirect_stderr(io.StringIO()):
                    # Force garbage collection to help with cleanup
                    import gc
                    gc.collect()
                    
                    # Additional cleanup for Windows
                    try:
                        import os
                        import tempfile
                        # Clean up any remaining temp files
                        temp_dir = os.environ.get('PYDOLL_TEMP_DIR', tempfile.gettempdir())
                        if os.path.exists(temp_dir):
                            # Just ignore any cleanup errors
                            pass
                    except:
                        pass
                
    async def _detect_cloudflare_protection(self, tab) -> bool:
        """
        Detect if there's Cloudflare protection on the current page.
        
        Args:
            tab: Browser tab instance
            
        Returns:
            True if Cloudflare protection is detected, False otherwise
        """
        try:
            html_content = await tab.page_source
            if not html_content or not html_content.strip().startswith('<'):
                return False
                
            tree = html.fromstring(html_content)
            
            # Check for Cloudflare protection indicators in title
            title_elements = tree.xpath("//title")
            if title_elements:
                title = title_elements[0].text_content().strip()
                protection_titles = [
                    "请稍候",
                    "Just a moment",
                    "Checking your browser",
                    "Please wait"
                ]
                
                for protection_title in protection_titles:
                    if protection_title in title:
                        return True
            
            # Check for Cloudflare challenge text
            page_text = tree.text_content().lower()
            challenge_texts = [
                "请完成以下操作，验证您是真人",
                "请稍候",
                "just a moment",
                "checking your browser",
                "verify you are human",
                "complete the challenge"
            ]
            
            for text in challenge_texts:
                if text.lower() in page_text:
                    return True
                        
            return False
            
        except Exception as e:
            print(f"   Warning: Could not detect Cloudflare protection: {e}")
            return False
    
    async def _attempt_cloudflare_bypass(self, tab):
        """
        Attempt to automatically bypass Cloudflare Turnstile captcha.
        
        Args:
            tab: Browser tab instance
        """
        # # Enable automatic Cloudflare Turnstile captcha bypass
        # try:
        #     async with tab.expect_and_bypass_cloudflare_captcha(
        #         custom_selector=(By.XPATH, '//p[contains(@class, "h2") and contains(@class, "spacer-bottom")]//following-sibling::div[1]//div'),
        #         time_before_click=2, time_to_wait_captcha=5):
        #         print(f"   ✅ Successfully bypassed Cloudflare Turnstile captcha")
        #     # await tab._bypass_cloudflare(event=None, custom_selector=(By.XPATH, '//p[contains(@class, "h2") and contains(@class, "spacer-bottom")]//following-sibling::div[1]//div'), time_before_click=2, time_to_wait_captcha=5)
        # except Exception as e:
        #     print(f"   ⚠️ Failed to automatically bypass Cloudflare Turnstile captcha. {e}")
        print(f"   ⏳ Attempting to automatically bypass Cloudflare Turnstile captcha...")
        try:
            selector = (By.XPATH, '//input[@name="cf-turnstile-response"]//parent::div')
            element = await tab.find_or_wait_element(
                *selector, timeout=1, raise_exc=False
            )
            print(f"   ✅ Find Cloudflare Turnstile captcha element: {element}")
            # print(f"   ✅ Cloudflare Turnstile captcha element type: {type(element)}")
            if element:
                if isinstance(element, list):
                    element = element[0]
                element = cast(WebElement, element)
                # adjust the external div size to shadow root width (usually 300px)
                await tab.execute_script('argument.style="width: 300px"', element)
                # await asyncio.sleep(5)
                await element.click(x_offset=-130)
                print(f"   ✅ Click input checkbox")
        except Exception as exc:
            print(f"   ⚠️ Error in cloudflare bypass: {exc}")

    async def _handle_cloudflare_protection(self, tab, page_description: str):
        """
        Handle Cloudflare protection by waiting for user intervention.
        
        Args:
            tab: Browser tab instance
            page_description: Description of the page being loaded
        """
        max_wait_time = CLOUDFLARE_MAX_WAIT_TIME
        check_interval = CLOUDFLARE_CHECK_INTERVAL
        waited_time = 0
        
        while waited_time < max_wait_time:
            try:
                # Get page title by parsing HTML content
                html_content = await tab.page_source
                if html_content and html_content.strip().startswith('<'):
                    tree = html.fromstring(html_content)
                    title_elements = tree.xpath("//title")
                    title = title_elements[0].text_content().strip() if title_elements else ""
                else:
                    title = ""
                
                # Check if title indicates Cloudflare protection
                if title and ("请稍候" in title or "Just a moment" in title or "Checking your browser" in title):
                    if waited_time == 0:
                        print(f"⚠️  Cloudflare protection detected on {page_description}")
                        print(f"   Page title: {title}")
                        print("   🔒 Please complete the verification manually in the browser window")
                        print("   💡 Look for:")
                        print("      - Checkbox with 'I'm human' or 'I'm not a robot'")
                        print("      - Turnstile challenge widget")
                        print("      - Any verification button or challenge")
                        print("   ⏳ The script will wait up to 2 minutes for you to complete the verification...")
                    
                    # Show progress every 15 seconds
                    if waited_time % 15 == 0 or waited_time < 10:
                        print(f"   ⏳ Waiting for verification... ({waited_time}s/{max_wait_time}s)")
                    
                    await asyncio.sleep(check_interval)
                    waited_time += check_interval
                    
                    # Attempt automatic Cloudflare Turnstile captcha bypass
                    await self._attempt_cloudflare_bypass(tab)
                else:
                    # Title doesn't indicate Cloudflare protection, we're good
                    if waited_time > 0:
                        print(f"   ✅ Verification completed! Waiting for page to fully load...")
                        # 额外等待页面完全加载，特别是第一个页面
                        await asyncio.sleep(5)
                    break
                    
            except Exception as e:
                print(f"   Warning: Could not check page title: {e}")
                await asyncio.sleep(check_interval)
                waited_time += check_interval
        
        if waited_time >= max_wait_time:
            print(f"   ⚠️  Timeout waiting for Cloudflare verification on {page_description}")
            print("   You may need to manually refresh the page or try again later.")
            print("   💡 Try running the command again - sometimes Cloudflare protection is temporary")
                
    async def get_chapter_links(self, menu_url: str) -> List[Tuple[str, str]]:
        """
        Extract chapter links from the menu page, handling pagination if configured.
        
        Args:
            menu_url: URL of the novel's menu/chapter list page
            
        Returns:
            List of tuples (chapter_url, chapter_title)
        """
        all_chapters = []
        visited_urls = set()  # Track visited URLs to prevent infinite loops
        current_url = menu_url
        page_num = 1
        
        print(f"Starting chapter extraction from: {menu_url}")
        
        while current_url:
            print(f"Processing page {page_num}: {current_url}")
            
            # Check if we've already visited this URL (prevent infinite loops)
            if current_url in visited_urls:
                print(f"⚠️  URL already visited, stopping pagination: {current_url}")
                break
            visited_urls.add(current_url)
            
            # Extract chapters from current page
            page_chapters = await self._extract_chapters_from_page(current_url)
            if page_chapters:
                all_chapters.extend(page_chapters)
                print(f"Found {len(page_chapters)} chapters on page {page_num}")
            else:
                print(f"Warning: No chapters found on page {page_num}")
            
            # Check for next page if pagination is configured
            if self.chapter_list_pagination_xpath:
                next_url = await self._get_next_page_url(current_url)
                if next_url and next_url != current_url:
                    current_url = next_url
                    page_num += 1
                    print(f"Found next page: {current_url}")
                else:
                    print("No more pages found, pagination complete")
                    break
            else:
                # No pagination configured, only process first page
                break
        
        print(f"Total chapters extracted: {len(all_chapters)} from {page_num} pages")
        return all_chapters
    
    async def _extract_chapters_from_page(self, page_url: str) -> List[Tuple[str, str]]:
        """
        Extract chapter links from a single page.
        
        Args:
            page_url: URL of the page to extract chapters from
            
        Returns:
            List of tuples (chapter_url, chapter_title)
        """
        tab = await self.browser.new_tab()
        try:
            print(f"  Extracting chapters from: {page_url}")
            await tab.go_to(page_url)
            
            # Wait a bit for the page to load
            await asyncio.sleep(2)
            
            # Check for Cloudflare protection
            await self._handle_cloudflare_protection(tab, "chapter list page")
            
            html_content = await tab.page_source
            
            # Check if we got valid HTML content
            if not html_content or len(html_content) < 100:
                print(f"Warning: Received short or empty content: {html_content[:200] if html_content else 'None'}")
                return []
            
            # Check if content looks like HTML
            if not html_content.strip().startswith('<'):
                # Check if it's a browser session ID (32 character hex string)
                if len(html_content.strip()) == 32 and all(c in '0123456789ABCDEF' for c in html_content.strip().upper()):
                    print(f"Warning: Received browser session ID instead of HTML content: {html_content}")
                    print("This might indicate a browser communication issue. Trying again...")
                    await asyncio.sleep(3)  # Wait longer
                    html_content = await tab.page_source
                    if not html_content.strip().startswith('<'):
                        print(f"Still receiving non-HTML content: {html_content[:200]}")
                        return []
                else:
                    print(f"Warning: Content doesn't appear to be HTML: {html_content[:200]}")
                    return []
            
            # Parse with lxml and apply XPath
            tree = html.fromstring(html_content)
            chapter_elements = tree.xpath(self.chapter_xpath)
            
            print(f"  Found {len(chapter_elements)} chapter elements with XPath: {self.chapter_xpath}")
            
            chapters = []
            for i, element in enumerate(chapter_elements):
                try:
                    if hasattr(element, 'get'):
                        # Element is an HTML element
                        href = element.get('href', '')
                        title = element.text_content().strip()
                    else:
                        # Element might be a string or other type
                        print(f"Warning: Element {i} is not an HTML element: {type(element)}")
                        continue
                        
                    if href and title:
                        # Convert relative URLs to absolute
                        full_url = urljoin(page_url, href)
                        chapters.append((full_url, title))
                    else:
                        print(f"Warning: Element {i} missing href or title: href='{href}', title='{title}'")
                        
                except Exception as e:
                    print(f"Error processing element {i}: {e}")
                    continue
                    
            return chapters
            
        except Exception as e:
            print(f"Error extracting chapters from page: {e}")
            return []
        finally:
            try:
                await tab.close()
            except (KeyError, Exception) as e:
                # Tab might already be closed or session ID changed
                print(f"Warning: Could not close tab cleanly: {e}")
                pass
    
    async def _get_next_page_url(self, current_url: str) -> Optional[str]:
        """
        Get the next page URL from the current page.
        
        Args:
            current_url: URL of the current page
            
        Returns:
            Next page URL if found, None otherwise
        """
        if not self.chapter_list_pagination_xpath:
            return None
            
        tab = await self.browser.new_tab()
        try:
            print(f"  Checking for next page: {current_url}")
            await tab.go_to(current_url)
            
            # Wait a bit for the page to load
            await asyncio.sleep(1)
            
            # Check for Cloudflare protection
            await self._handle_cloudflare_protection(tab, "next page check")
            
            html_content = await tab.page_source
            
            # Check if we got valid HTML content
            if not html_content or len(html_content) < 100:
                print(f"Warning: Received short or empty content for next page check: {html_content[:200] if html_content else 'None'}")
                return None
            
            # Check if content looks like HTML
            if not html_content.strip().startswith('<'):
                print(f"Warning: Content doesn't appear to be HTML for next page check: {html_content[:200]}")
                return None
            
            # Parse with lxml and apply XPath
            tree = html.fromstring(html_content)
            pagination_elements = tree.xpath(self.chapter_list_pagination_xpath)
            
            print(f"  Found {len(pagination_elements)} pagination elements with XPath: {self.chapter_list_pagination_xpath}")
            
            for element in pagination_elements:
                try:
                    if hasattr(element, 'get'):
                        # Element is an HTML element
                        href = element.get('href', '')
                        if href:
                            # Convert relative URLs to absolute
                            next_url = urljoin(current_url, href)
                            if next_url != current_url:  # Make sure it's different
                                print(f"  Found next page URL: {next_url}")
                                return next_url
                    else:
                        print(f"Warning: Pagination element is not an HTML element: {type(element)}")
                        continue
                        
                except Exception as e:
                    print(f"Error processing pagination element: {e}")
                    continue
            
            print("  No next page found")
            return None
            
        except Exception as e:
            print(f"Error checking for next page: {e}")
            return None
        finally:
            try:
                await tab.close()
            except (KeyError, Exception) as e:
                # Tab might already be closed or session ID changed
                print(f"Warning: Could not close tab cleanly: {e}")
                pass
    
    async def get_chapter_pagination_links(self, chapter_url: str) -> List[str]:
        """
        Extract pagination links from a chapter page.
        
        Args:
            chapter_url: URL of the chapter page
            
        Returns:
            List of pagination URLs for this chapter
        """
        if not self.chapter_pagination_xpath:
            return [chapter_url]  # No pagination, return original URL
            
        tab = await self.browser.new_tab()
        try:
            print(f"Checking for pagination in chapter: {chapter_url}")
            await tab.go_to(chapter_url)
            
            # Wait for page to load
            await asyncio.sleep(1)
            
            # Check for Cloudflare protection
            await self._handle_cloudflare_protection(tab, f"chapter pagination check")
            
            html_content = await tab.page_source
            
            # Check if we got valid HTML content
            if not html_content or len(html_content) < 100:
                print(f"Warning: Received short or empty content for pagination check: {html_content[:200] if html_content else 'None'}")
                return [chapter_url]
            
            # Check if content looks like HTML
            if not html_content.strip().startswith('<'):
                print(f"Warning: Content doesn't appear to be HTML for pagination check: {html_content[:200]}")
                return [chapter_url]
            
            # Parse with lxml and apply XPath
            tree = html.fromstring(html_content)
            pagination_elements = tree.xpath(self.chapter_pagination_xpath)
            
            print(f"Found {len(pagination_elements)} pagination elements with XPath: {self.chapter_pagination_xpath}")
            
            pagination_urls = [chapter_url]  # Start with original URL
            for element in pagination_elements:
                try:
                    if hasattr(element, 'get'):
                        # Element is an HTML element
                        href = element.get('href', '')
                        if href and href != chapter_url:  # Avoid duplicates
                            # Convert relative URLs to absolute
                            full_url = urljoin(chapter_url, href)
                            if full_url not in pagination_urls:
                                pagination_urls.append(full_url)
                    else:
                        # Element might be a string or other type
                        print(f"Warning: Pagination element is not an HTML element: {type(element)}")
                        continue
                        
                except Exception as e:
                    print(f"Error processing pagination element: {e}")
                    continue
            
            print(f"Found {len(pagination_urls)} total pages for this chapter")
            return pagination_urls
            
        except Exception as e:
            print(f"Error extracting pagination links: {e}")
            return [chapter_url]  # Fallback to original URL
        finally:
            try:
                await tab.close()
            except (KeyError, Exception) as e:
                print(f"Warning: Could not close tab cleanly: {e}")
                pass
            
    async def download_chapter(self, chapter_url: str, chapter_title: str, base_url: str, metadata_hash: str = None) -> bool:
        """
        Download a single chapter, handling pagination if configured.
        
        Args:
            chapter_url: URL of the chapter
            chapter_title: Title of the chapter
            base_url: Base URL for relative link resolution
            metadata_hash: Hash of the metadata file to organize chapters by source
            
        Returns:
            True if successful, False otherwise
        """
        # Sanitize filename - use only the chapter title
        safe_title = sanitize_filename(chapter_title)
        
        # Create organized directory structure based on metadata hash
        if metadata_hash:
            # Create subdirectory for this metadata hash
            hash_dir = chapters_dir / f"chapters_{metadata_hash}"
            hash_dir.mkdir(exist_ok=True)
            chapter_file = hash_dir / f"{safe_title}.html"
        else:
            # Fallback to original behavior for backward compatibility
            chapter_file = chapters_dir / f"{safe_title}.html"
        
        # Check if chapter already exists
        if chapter_file.exists():
            print(f"Skipping existing chapter: {chapter_title}")
            return True
            
        async with self.semaphore:
            try:
                print(f"Downloading chapter: {chapter_title}")
                
                # Get all pagination URLs for this chapter
                pagination_urls = await self.get_chapter_pagination_links(chapter_url)
                
                if len(pagination_urls) > 1:
                    print(f"Found {len(pagination_urls)} pages for chapter: {chapter_title}")
                else:
                    print(f"Single page chapter: {chapter_title}")
                
                # Download content from all pages
                all_content = []
                for i, page_url in enumerate(pagination_urls):
                    page_content = await self._download_chapter_page(page_url, chapter_title, i + 1, len(pagination_urls))
                    if page_content:
                        all_content.append(page_content)
                    else:
                        print(f"❌ 章节下载失败: {chapter_title}")
                        print(f"   失败页面: {i + 1}/{len(pagination_urls)}")
                
                if not all_content:
                    print(f"❌ 章节内容为空: {chapter_title}")
                    print(f"💡 可能原因: 页面无法访问或内容提取失败")
                    return False
                
                # Combine all page content
                combined_content = "\n\n".join(all_content)
                
                # Process content with regex and string replacements
                processed_content = self._process_content(combined_content)
                
                # Save chapter content
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    f.write(f"<h1>{chapter_title}</h1>\n")
                    f.write(f"<div class='chapter-content'>\n")
                    f.write(processed_content)
                    f.write("</div>\n")
                    
                print(f"Downloaded: {chapter_title} ({len(pagination_urls)} pages)")
                return True
                
            except Exception as e:
                print(f"❌ 章节下载异常: {chapter_title}")
                print(f"   错误详情: {e}")
                return False
    
    async def _validate_url(self, url: str) -> tuple[bool, str]:
        """
        Validate if a URL is accessible before attempting to download.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic URL format validation
            if not url or not url.startswith(('http://', 'https://')):
                return False, "❌ 无效的URL格式"
            
            # Try to access the URL with a quick check
            tab = await self.browser.new_tab()
            try:
                await tab.go_to(url)
                await asyncio.sleep(2)  # Wait a bit longer for page to load
                html_content = await tab.page_source
                
                # Check for various error conditions
                if not html_content or len(html_content) < 50:
                    return False, "❌ 页面无法访问 - 可能网络连接问题或代理未开启"
                
                if "page not found" in html_content.lower() or "404" in html_content:
                    return False, "❌ 页面未找到 (404) - 章节链接可能已失效"
                
                if "access denied" in html_content.lower() or "forbidden" in html_content.lower():
                    return False, "❌ 访问被拒绝 - 可能需要代理或网站限制访问"
                
                if "timeout" in html_content.lower() or "timed out" in html_content.lower():
                    return False, "❌ 页面访问超时 - 网络连接不稳定"
                
                if "cloudflare" in html_content.lower() and "checking your browser" in html_content.lower():
                    return False, "❌ 页面被Cloudflare保护 - 正在验证浏览器"
                
                # Check if content looks like an error page
                if len(html_content) < 200 and any(keyword in html_content.lower() for keyword in ["error", "not found", "unavailable"]):
                    return False, "❌ 页面返回错误信息 - 可能网站维护或链接失效"
                
                return True, ""
                
            finally:
                try:
                    await tab.close()
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"❌ 页面访问失败: {str(e)}"
            if "proxy" in str(e).lower() or "connection" in str(e).lower():
                error_msg += " - 请检查代理设置"
            elif "timeout" in str(e).lower():
                error_msg += " - 网络连接超时"
            return False, error_msg

    async def _download_chapter_page(self, page_url: str, chapter_title: str, page_num: int, total_pages: int) -> Optional[str]:
        """
        Download content from a single page of a chapter.
        
        Args:
            page_url: URL of the page
            chapter_title: Title of the chapter
            page_num: Page number (1-based)
            total_pages: Total number of pages
            
        Returns:
            Content text if successful, None otherwise
        """
        # Note: URL validation is skipped to avoid double page loading
        # The page will be validated during the actual download process
        
        tab = await self.browser.new_tab()
        try:
            if total_pages > 1:
                print(f"  Downloading page {page_num}/{total_pages}: {page_url}")
            else:
                print(f"  Downloading: {page_url}")
            
            await tab.go_to(page_url)
            
            # Wait for page to load
            await asyncio.sleep(1)
            
            # Check for Cloudflare protection
            await self._handle_cloudflare_protection(tab, f"chapter page {page_num}")
            
            html_content = await tab.page_source
            
            # Check if we got valid HTML content
            if not html_content or len(html_content) < 100:
                print(f"❌ 页面内容过短或为空")
                print(f"   页面: {page_url}")
                print(f"   内容预览: {html_content[:100] if html_content else '无内容'}")
                return None
            
            # Check for common error pages with specific error messages
            if "page not found" in html_content.lower() or "404" in html_content:
                print(f"❌ 页面未找到 (404)")
                print(f"   页面: {page_url}")
                print(f"💡 可能原因: 章节链接已失效，请重新解析章节")
                return None
            
            if "access denied" in html_content.lower() or "forbidden" in html_content.lower():
                print(f"❌ 访问被拒绝")
                print(f"   页面: {page_url}")
                print(f"💡 可能原因: 需要代理访问或网站限制访问")
                return None
            
            if "timeout" in html_content.lower() or "timed out" in html_content.lower():
                print(f"❌ 页面访问超时")
                print(f"   页面: {page_url}")
                print(f"💡 可能原因: 网络连接不稳定，请稍后重试")
                return None
            
            # Check if content looks like HTML
            if not html_content.strip().startswith('<'):
                # Check if it's a browser session ID (32 character hex string)
                if len(html_content.strip()) == 32 and all(c in '0123456789ABCDEF' for c in html_content.strip().upper()):
                    print(f"Warning: Received browser session ID instead of HTML content for page {page_num}: {html_content}")
                    print("This might indicate a browser communication issue. Trying again...")
                    await asyncio.sleep(2)  # Wait longer
                    html_content = await tab.page_source
                    if not html_content.strip().startswith('<'):
                        print(f"Still receiving non-HTML content for page {page_num}: {html_content[:200]}")
                        return None
                else:
                    print(f"Warning: Content doesn't appear to be HTML for page {page_num}: {html_content[:200]}")
                    return None
            
            # Parse with lxml and apply XPath
            tree = html.fromstring(html_content)
            content_elements = tree.xpath(self.content_xpath)
            
            # 添加调试信息
            print(f"  Debug: Page {page_num} content length: {len(html_content)}")
            print(f"  Debug: XPath '{self.content_xpath}' found {len(content_elements)} elements")
            
            if not content_elements:
                print(f"Warning: No content found for page {page_num} of chapter: {chapter_title}")
                # 尝试查找页面中的其他可能的内容容器
                all_divs = tree.xpath('//div[@class]')
                print(f"  Debug: Page has {len(all_divs)} div elements with class attributes")
                for i, div in enumerate(all_divs[:5]):
                    class_name = div.get('class', '')
                    print(f"    {i+1}. class='{class_name}'")
                return None
            
            # Extract text content
            content_text = ""
            for element in content_elements:
                if hasattr(element, 'text_content'):
                    # Element object
                    content_text += element.text_content() + "\n"
                else:
                    # Text node or other type
                    content_text += str(element) + "\n"
            
            return content_text.strip()
            
        except Exception as e:
            print(f"❌ 页面下载异常: {chapter_title} (第{page_num}页)")
            print(f"   错误详情: {e}")
            return None
        finally:
            try:
                await tab.close()
            except (KeyError, Exception) as e:
                # Tab might already be closed or session ID changed
                print(f"Warning: Could not close tab cleanly for page {page_num}: {e}")
                pass
                
    async def parse_chapters(self, menu_url: str) -> List[Tuple[str, str]]:
        """
        Parse chapter information from URL and save to storage.
        
        Args:
            menu_url: URL of the novel's menu/chapter list page
            
        Returns:
            List of (chapter_url, chapter_title) tuples
        """
        print(f"Parsing chapter information from: {menu_url}")
        
        try:
            # Get chapter links
            print("Extracting chapter links...")
            chapters = await self.get_chapter_links(menu_url)
            print(f"Found {len(chapters)} chapters")
            
            if not chapters:
                print("No chapters found. Please check your XPath expressions.")
                return []
            
            # Save chapter metadata
            self.metadata_manager.save_chapter_metadata(
                menu_url, chapters, self.chapter_xpath, self.content_xpath, 
                self.chapter_pagination_xpath, self.chapter_list_pagination_xpath,
                self.content_regex, self.string_replacements
            )
            
            # Show first few chapters for debugging
            print("First 5 chapters:")
            for i, (url, title) in enumerate(chapters[:5]):
                print(f"  {i+1}. {title} -> {url}")
                
            return chapters
            
        except Exception as e:
            print(f"Error in parse_chapters: {e}")
            import traceback
            traceback.print_exc()
            return []
            
    async def download_novel(self, menu_url: str, force_parse: bool = False) -> Dict[str, Any]:
        """
        Download all chapters of a novel.
        Automatically checks for stored chapter information and parses from URL if needed.
        
        Args:
            menu_url: URL of the novel's menu/chapter list page
            force_parse: Whether to force parsing from URL even if stored data exists
            
        Returns:
            Dictionary with download statistics
        """
        print(f"Starting novel download from: {menu_url}")
        
        try:
            chapters = []
            
            # Check for stored chapter information first (unless force_parse is True)
            if not force_parse:
                print("Checking for stored chapter information...")
                stored_chapters = self.metadata_manager.get_stored_chapters(menu_url)
                if stored_chapters:
                    print(f"✅ Found stored chapter information with {len(stored_chapters)} chapters")
                    chapters = stored_chapters
                else:
                    print("📋 No stored chapter information found. Will parse from URL...")
            
            # If no stored chapters or force_parse is True, parse from URL
            if not chapters:
                print("🔍 Extracting chapter links from URL...")
                chapters = await self.get_chapter_links(menu_url)
                if chapters:
                    print(f"✅ Successfully parsed {len(chapters)} chapters from URL")
                    # Save the parsed chapters for future use
                    self.metadata_manager.save_chapter_metadata(
                        menu_url, chapters, self.chapter_xpath, self.content_xpath, 
                        self.chapter_pagination_xpath, self.chapter_list_pagination_xpath,
                        self.content_regex, self.string_replacements
                    )
                    print("💾 Chapter information saved for future downloads")
                else:
                    print("❌ No chapters found. Please check your XPath expressions.")
                    return {"total": 0, "downloaded": 0, "skipped": 0, "failed": 0, "error": "No chapters found"}
            
            print(f"📚 Found {len(chapters)} chapters total")
            
            # Get metadata hash for organizing chapters
            metadata_hash = self.metadata_manager.get_metadata_hash(menu_url)
            if metadata_hash:
                print(f"📁 Organizing chapters in directory: chapters_{metadata_hash}/")
            else:
                print("📁 No metadata hash found, using default chapters directory")
            
            # Show first few chapters for debugging
            print("📖 First 5 chapters:")
            for i, chapter_info in enumerate(chapters[:5]):
                if len(chapter_info) == 3:
                    # New format with index
                    url, title, chapter_index = chapter_info
                else:
                    # Old format without index
                    url, title = chapter_info
                print(f"  {i+1}. {title} -> {url}")
            
            # Download chapters concurrently
            print(f"⬇️  Starting download with {self.concurrency} concurrent connections...")
            tasks = []
            for chapter_info in chapters:
                if len(chapter_info) == 3:
                    # New format with index
                    chapter_url, chapter_title, chapter_index = chapter_info
                else:
                    # Old format without index
                    chapter_url, chapter_title = chapter_info
                
                task = self.download_chapter(chapter_url, chapter_title, menu_url, metadata_hash)
                tasks.append(task)
                
            print("⏳ Waiting for download tasks to complete...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            print("✅ Download tasks completed")
            
            # Count results
            stats = {"total": len(chapters), "downloaded": 0, "skipped": 0, "failed": 0}
            for result in results:
                if isinstance(result, Exception):
                    print(f"❌ Exception in download task: {result}")
                    stats["failed"] += 1
                elif result is True:
                    stats["downloaded"] += 1
                else:
                    stats["failed"] += 1
                    
            return stats
            
        except Exception as e:
            print(f"❌ Error in download_novel: {e}")
            import traceback
            traceback.print_exc()
            return {"total": 0, "downloaded": 0, "skipped": 0, "failed": 0}
