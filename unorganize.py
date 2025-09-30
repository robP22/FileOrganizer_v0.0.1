#!/usr/bin/env python3
"""
Quick and dirty unorganizer script for testing purposes.
Unorganizes organized directory structure back into a single messy folder.
"""

import os
import shutil
from pathlib import Path
import argparse

def unorganize_directory(organized_dir: Path, output_dir: Path):
    """
    Recursively find all files in organized directory and dump them into a flat output directory.
    """
    organized_dir = Path(organized_dir)
    output_dir    = Path(output_dir)
    
    if not organized_dir.exists():
        print(f"Error: Source directory {organized_dir} does not exist")
        return
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    files_moved = 0
    
    # Walk through all subdirectories and find files
    for root, dirs, files in os.walk(organized_dir):
        for file in files:
            source_file      = Path(root) / file
            destination_file = output_dir / file
            
            # Handle filename conflicts by adding counter
            counter = 1
            while destination_file.exists():
                stem             = Path(file).stem
                suffix           = Path(file).suffix
                destination_file = output_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            try:
                shutil.move(str(source_file), str(destination_file))
                print(f"Moved: {source_file} -> {destination_file}")
                files_moved += 1
            except Exception as e:
                print(f"Error moving {source_file}: {e}")
    
    print(f"\nUnorganize done. Moved {files_moved} files to {output_dir}.")
    
    # Clean up empty directories
    cleanup_empty_dirs(organized_dir)


def cleanup_empty_dirs(directory: Path):
    """Remove empty directories after unorganizing."""
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()):  # Directory is empty
                    dir_path.rmdir()
                    print(f"Removed empty directory: {dir_path}")
            except OSError:
                pass  # Directory not empty or other error


def main():
    parser = argparse.ArgumentParser(description="Unorganize files back into a flat directory")
    parser.add_argument("source", help="Directory to unorganize")
    parser.add_argument("output", help="Directory for storage")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be moved")
        # TODO: Implement dry run logic
        return
    
    print(f"Unorganizing files from {args.source} to {args.output}")
    
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    unorganize_directory(Path(args.source), Path(args.output))


if __name__ == "__main__":
    main()
