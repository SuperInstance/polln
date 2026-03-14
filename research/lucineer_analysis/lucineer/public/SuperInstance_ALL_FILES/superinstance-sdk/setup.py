"""
SuperInstance SDK Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="superinstance-sdk",
    version="0.1.0",
    author="SuperInstance.AI",
    author_email="sdk@superinstance.ai",
    description="SDK for SuperInstance mask-locked inference hardware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/superinstance-ai/superinstance-sdk",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.0",
            "mypy>=1.0",
            "ruff>=0.1.0",
        ],
        "serial": [
            "pyserial>=3.5",  # For USB serial communication on Windows
        ],
    },
    entry_points={
        "console_scripts": [
            "superinstance=superinstance.cli:main",
        ],
    },
    keywords="ai llm inference hardware edge superinstance",
    project_urls={
        "Documentation": "https://docs.superinstance.ai",
        "Source": "https://github.com/superinstance-ai/superinstance-sdk",
        "Tracker": "https://github.com/superinstance-ai/superinstance-sdk/issues",
    },
)
