#!/usr/bin/env python3
"""
Simple script to bump version using git tags.
Usage:
  python bump-version.py patch   # 0.7.1 -> 0.7.2
  python bump-version.py minor   # 0.7.1 -> 0.8.0
  python bump-version.py major   # 0.7.1 -> 1.0.0
"""

import subprocess
import sys

from packaging import version


def get_latest_tag():
    """Get the latest git tag."""
    try:
        result = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "0.0.0"


def bump_version(current_version, bump_type):
    """Bump version based on type."""
    v = version.Version(current_version)

    if bump_type == "patch":
        new_version = f"{v.major}.{v.minor}.{v.micro + 1}"
    elif bump_type == "minor":
        new_version = f"{v.major}.{v.minor + 1}.0"
    elif bump_type == "major":
        new_version = f"{v.major + 1}.0.0"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return new_version


def create_tag(new_version):
    """Create and push new git tag."""
    tag_name = f"v{new_version}"

    # Create tag
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {new_version}"], check=True)

    # Push tag
    subprocess.run(["git", "push", "origin", tag_name], check=True)

    print(f"Created and pushed tag: {tag_name}")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["patch", "minor", "major"]:
        print(__doc__)
        sys.exit(1)

    bump_type = sys.argv[1]

    # Get current version from latest tag
    current_tag = get_latest_tag()
    current_version = current_tag.lstrip("v") if current_tag.startswith("v") else current_tag

    print(f"Current version: {current_version}")

    # Bump version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")

    # Confirm
    response = input(f"Create tag v{new_version}? (y/N): ")
    if response.lower() != "y":
        print("Cancelled")
        sys.exit(0)

    # Create tag
    create_tag(new_version)
    print(f"Version bumped to {new_version}")


if __name__ == "__main__":
    main()
