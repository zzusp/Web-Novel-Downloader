#!/usr/bin/env python3
"""
Setup script for Book Downloader.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="web-novel-downloader",
    version="0.0.2",
    author="Book Downloader Team",
    author_email="645541506@qq.com",
    description="A tool for downloading novels from web pages with configurable XPath expressions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zzusp/Web-Novel-Downloader",
    project_urls={
        "Bug Reports": "https://github.com/zzusp/Web-Novel-Downloader/issues",
        "Source": "https://github.com/zzusp/Web-Novel-Downloader",
    },
    packages=find_packages(),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "web-novel-downloader=scripts.book_downloader:main",
            "web-novel-scraper=scripts.scraper:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
