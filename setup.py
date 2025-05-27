from setuptools import setup, find_packages
import os

# Read README.md if it exists, otherwise use a default description
long_description = "A mindful terminal chat application"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="dhammashell",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "colorama>=0.4.6",
        "textblob>=0.17.1",
        "prompt_toolkit>=3.0.43",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "requests>=2.31.0",  # For MiddleSeek API calls
    ],
    entry_points={
        "console_scripts": [
            "ds=dhammashell.main:main",
        ],
    },
    author="DhammaShell Team",
    author_email="contact@dhammashell.org",
    description="A mindful terminal chat application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dhammashell",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    package_data={
        "dhammashell": ["py.typed"],
        "middleseek": ["py.typed"],
    },
) 