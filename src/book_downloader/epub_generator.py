#!/usr/bin/env python3
"""
EPUB generation module for Novel Downloader.
Handles creation of EPUB files from downloaded chapters.
"""

import os
import re
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List

from .config import temp_dir
from .utils import extract_chapter_title, sort_chapters_by_metadata
from .metadata import find_best_metadata


def create_epub(output_file: str, title: str, author: str, chapter_files: List[Path], reverse: bool = False):
    """
    Create an EPUB file from chapters.
    
    Args:
        output_file: Output filename for the EPUB
        title: Title for the novel
        author: Author name
        chapter_files: List of chapter file paths
        reverse: Whether to merge in reverse order
    """
    # Ensure output file has .epub extension
    if not output_file.endswith('.epub'):
        output_file = output_file.rsplit('.', 1)[0] + '.epub'
    
    # Find and load metadata from chapters/metadata/ directory
    metadata = find_best_metadata()
    if not metadata:
        return
    
    # Use metadata for chapter ordering
    print(f"Using metadata-based chapter ordering ({'reverse' if reverse else 'normal'} order)...")
    chapter_files = sort_chapters_by_metadata(chapter_files, metadata["chapters"], reverse)
    
    # Create temporary directory for EPUB contents
    temp_epub_dir = Path(temp_dir) / "epub_temp"
    temp_epub_dir.mkdir(exist_ok=True)
    
    try:
        # Create META-INF directory
        meta_inf_dir = temp_epub_dir / "META-INF"
        meta_inf_dir.mkdir(exist_ok=True)
        
        # Create container.xml
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
        with open(meta_inf_dir / "container.xml", 'w', encoding='utf-8') as f:
            f.write(container_xml)
        
        # Create OEBPS directory
        oebps_dir = temp_epub_dir / "OEBPS"
        oebps_dir.mkdir(exist_ok=True)
        
        # Create mimetype file
        with open(temp_epub_dir / "mimetype", 'w', encoding='utf-8') as f:
            f.write("application/epub+zip")
        
        # Create content.opf
        create_content_opf(oebps_dir, title, author, chapter_files)
        
        # Create toc.ncx
        create_toc_ncx(oebps_dir, title, chapter_files)
        
        # Create chapter files
        create_epub_chapters(oebps_dir, chapter_files, title, author)
        
        # Create EPUB file
        create_epub_zip(output_file, temp_epub_dir)
        
    finally:
        # Clean up temporary directory
        import shutil
        if temp_epub_dir.exists():
            shutil.rmtree(temp_epub_dir)


def create_content_opf(oebps_dir: Path, title: str, author: str, chapter_files: List[Path]):
    """Create content.opf file for EPUB."""
    manifest_items = []
    spine_items = []
    
    # Add cover and title page
    manifest_items.append('    <item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>')
    manifest_items.append('    <item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>')
    spine_items.append('    <itemref idref="cover"/>')
    spine_items.append('    <itemref idref="title"/>')
    
    # Add chapters
    for i, chapter_file in enumerate(chapter_files):
        chapter_title = extract_chapter_title(chapter_file)
        # Create a safe filename from chapter title
        safe_filename = re.sub(r'[<>:"/\\|?*（）]', '_', chapter_title)
        safe_filename = safe_filename.replace(' ', '_')[:50]  # Limit length
        # Ensure filename is ASCII safe
        safe_filename = safe_filename.encode('ascii', 'ignore').decode('ascii')
        if not safe_filename:
            safe_filename = f"chapter_{i+1:03d}"
        
        # Create XML-safe ID from chapter title (keep Chinese characters but make XML safe)
        xml_safe_id = re.sub(r'[<>:"/\\|?*]', '_', chapter_title)
        xml_safe_id = xml_safe_id.replace(' ', '_')[:50]  # Limit length
        if not xml_safe_id:
            xml_safe_id = f"chapter_{i+1:03d}"
        
        chapter_href = f"{safe_filename}.xhtml"
        manifest_items.append(f'    <item id="{xml_safe_id}" href="{chapter_href}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'    <itemref idref="{xml_safe_id}"/>')
    
    content_opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="book-id" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{title}</dc:title>
        <dc:creator opf:file-as="{author}" opf:role="aut">{author}</dc:creator>
        <dc:language>zh-CN</dc:language>
        <dc:identifier id="book-id" opf:scheme="UUID">urn:uuid:{uuid.uuid4().hex}</dc:identifier>
        <dc:date>{datetime.now().strftime('%Y-%m-%d')}</dc:date>
        <meta name="generator" content="Novel Downloader"/>
    </metadata>
    <manifest>
{chr(10).join(manifest_items)}
    </manifest>
    <spine toc="ncx">
{chr(10).join(spine_items)}
    </spine>
    <guide>
        <reference type="cover" title="Cover" href="cover.xhtml"/>
        <reference type="text" title="Start" href="title.xhtml"/>
    </guide>
</package>'''
    
    with open(oebps_dir / "content.opf", 'w', encoding='utf-8') as f:
        f.write(content_opf)


def create_toc_ncx(oebps_dir: Path, title: str, chapter_files: List[Path]):
    """Create toc.ncx file for EPUB."""
    nav_points = []
    
    for i, chapter_file in enumerate(chapter_files):
        # Extract actual chapter title from HTML file
        chapter_title = extract_chapter_title(chapter_file)
        # Create a safe filename from chapter title
        safe_filename = re.sub(r'[<>:"/\\|?*（）]', '_', chapter_title)
        safe_filename = safe_filename.replace(' ', '_')[:50]  # Limit length
        # Ensure filename is ASCII safe
        safe_filename = safe_filename.encode('ascii', 'ignore').decode('ascii')
        if not safe_filename:
            safe_filename = f"chapter_{i+1:03d}"
        
        # Create XML-safe ID from chapter title (keep Chinese characters but make XML safe)
        xml_safe_id = re.sub(r'[<>:"/\\|?*]', '_', chapter_title)
        xml_safe_id = xml_safe_id.replace(' ', '_')[:50]  # Limit length
        if not xml_safe_id:
            xml_safe_id = f"chapter_{i+1:03d}"
        
        nav_points.append(f'''        <navPoint id="{xml_safe_id}" playOrder="{i+2}">
            <navLabel><text>{chapter_title}</text></navLabel>
            <content src="{safe_filename}.xhtml"/>
        </navPoint>''')
    
    toc_ncx = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{uuid.uuid4().hex}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{title}</text>
    </docTitle>
    <navMap>
        <navPoint id="title" playOrder="1">
            <navLabel><text>Title Page</text></navLabel>
            <content src="title.xhtml"/>
        </navPoint>
{chr(10).join(nav_points)}
    </navMap>
</ncx>'''
    
    with open(oebps_dir / "toc.ncx", 'w', encoding='utf-8') as f:
        f.write(toc_ncx)


def create_epub_chapters(oebps_dir: Path, chapter_files: List[Path], title: str, author: str):
    """Create XHTML chapter files for EPUB."""
    # Create cover page
    cover_xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Cover</title>
    <style type="text/css">
        body { text-align: center; margin: 0; padding: 0; }
        .cover { height: 100vh; display: flex; flex-direction: column; justify-content: center; }
        h1 { font-size: 2em; margin: 0; }
        p { font-size: 1.2em; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="cover">
        <h1>Cover Page</h1>
        <p>This is a cover page</p>
    </div>
</body>
</html>'''
    
    with open(oebps_dir / "cover.xhtml", 'w', encoding='utf-8') as f:
        f.write(cover_xhtml)
    
    # Create title page with actual novel title
    title_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <style type="text/css">
        body {{ text-align: center; margin: 50px; font-family: serif; }}
        h1 {{ font-size: 2.5em; margin: 50px 0; }}
        h2 {{ font-size: 1.5em; margin: 30px 0; }}
        p {{ font-size: 1.2em; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <h2>作者: {author}</h2>
    <p>Generated by Novel Downloader</p>
</body>
</html>'''
    
    with open(oebps_dir / "title.xhtml", 'w', encoding='utf-8') as f:
        f.write(title_xhtml)
    
    # Create chapter files
    for i, chapter_file in enumerate(chapter_files):
        print(f"Creating EPUB chapter: {chapter_file.name}")
        
        with open(chapter_file, 'r', encoding='utf-8') as infile:
            content = infile.read()
        
        # Convert HTML to XHTML for EPUB
        from lxml import html
        tree = html.fromstring(content)
        
        # Extract title and content
        title_elems = tree.xpath('//h1')
        content_elems = tree.xpath('//div[@class="chapter-content"]')
        
        chapter_title = title_elems[0].text_content().strip() if len(title_elems) > 0 else chapter_file.stem
        chapter_content = content_elems[0].text_content().strip() if len(content_elems) > 0 else tree.text_content().strip()
        
        # Create a safe filename from chapter title
        safe_filename = re.sub(r'[<>:"/\\|?*（）]', '_', chapter_title)
        safe_filename = safe_filename.replace(' ', '_')[:50]  # Limit length
        # Ensure filename is ASCII safe
        safe_filename = safe_filename.encode('ascii', 'ignore').decode('ascii')
        if not safe_filename:
            safe_filename = f"chapter_{i+1:03d}"
        
        # Create XHTML chapter
        chapter_xhtml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{chapter_title}</title>
    <style type="text/css">
        body {{ font-family: serif; margin: 20px; line-height: 1.6; }}
        h1 {{ font-size: 1.5em; margin: 20px 0; text-align: center; }}
        p {{ margin: 10px 0; text-indent: 2em; }}
    </style>
</head>
<body>
    <h1>{chapter_title}</h1>
    <div class="chapter-content">
        {chapter_content.replace(chr(10), '<br/>')}
    </div>
</body>
</html>'''
        
        with open(oebps_dir / f"{safe_filename}.xhtml", 'w', encoding='utf-8') as f:
            f.write(chapter_xhtml)


def create_epub_zip(output_file: str, temp_dir: Path):
    """Create the final EPUB ZIP file."""
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
        # Add mimetype file first (uncompressed)
        epub_zip.write(temp_dir / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        
        # Add all other files
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file != "mimetype":  # Skip mimetype as it's already added
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(temp_dir)
                    epub_zip.write(file_path, arc_path)
