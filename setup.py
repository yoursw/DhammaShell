from setuptools import setup, find_packages
import os

# Read README.md if it exists, otherwise use a default description
long_description = "A mindful terminal chat application"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="dhammashell",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.6",
        "textblob>=0.17.1",
        "prompt_toolkit>=3.0.43",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "pydantic>=2.6.1",
        "python-dateutil>=2.8.2",
        "pytest>=8.0.0",
        "pytest-cov>=4.1.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "tabulate>=0.9.0",
        "pandas>=2.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ds=dhammashell.cli:main",
        ],
    },
    author="DhammaShell Team",
    author_email="team@dhammashell.org",
    description="A mindful terminal chat tool with empathy research capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dhammashell/dhammashell",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    package_data={
        "dhammashell": ["py.typed"],
        "middleseek": ["py.typed"],
    },
)
