#!/usr/bin/env python
"""Setup script for batch2md package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="batch2md",
    version="0.1.0",
    description="Batch convert documents to Markdown via PDF using MinerU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/batch2md",
    license="MIT",

    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    # Python version requirement
    python_requires=">=3.8",

    # Dependencies
    install_requires=[
        "mineru>=2.0.0",
    ],

    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },

    # Entry point for CLI
    entry_points={
        "console_scripts": [
            "batch2md=batch2md.main:main",
        ],
    },

    # Classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
    ],

    # Keywords
    keywords="markdown converter pdf docx pptx xlsx mineru batch",

    # Include package data
    include_package_data=True,
    zip_safe=False,
)
