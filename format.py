#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path
import glob


def run_command(cmd, cwd=None):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(cmd)}: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: Command not found. {e}", file=sys.stderr)
        sys.exit(1)


def check_prettier():
    """Check if prettier is installed and install it if needed."""
    try:
        subprocess.run(["prettier", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Prettier not found. Installing prettier...")
        try:
            subprocess.run(["npm", "install", "-g", "prettier"], check=True)
            print("Prettier installed successfully!")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(
                "Error: Could not install prettier. Please install Node.js and npm first.",
                file=sys.stderr,
            )
            print(
                "Visit https://nodejs.org/ to install Node.js and npm.", file=sys.stderr
            )
            sys.exit(1)


def find_files(pattern):
    """Find files matching the given pattern."""
    return glob.glob(pattern, recursive=True)


def format_with_prettier(file_type, patterns):
    """Format files with prettier if any matching files are found."""
    files = []
    for pattern in patterns:
        files.extend(find_files(pattern))

    if not files:
        print(f"No {file_type} files found to format.")
        return

    print(f"\nFormatting {file_type} files...")
    run_command(
        [
            "prettier",
            "--write",
            "--config",
            ".prettierrc",
            *files,
        ]
    )


def main():
    """Format all files in the project."""
    project_root = Path(__file__).parent

    # Format Python files with black
    print("Formatting Python files...")
    run_command(
        [
            "black",
            "--line-length",
            "88",  # black's default
            "--target-version",
            "py38",
            "dhammashell",
            "tests",
            "format.py",
            "setup.py",
        ]
    )

    # Check and install prettier if needed
    check_prettier()

    # Format different file types with prettier
    format_with_prettier("JSON", ["*.json", ".prettierrc"])
    format_with_prettier("Markdown", ["*.md"])
    format_with_prettier("YAML", ["*.yaml", "*.yml"])

    print("\nFormatting complete!")


if __name__ == "__main__":
    main()
