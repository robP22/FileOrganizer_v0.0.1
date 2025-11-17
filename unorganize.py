import os
import shutil
from pathlib import Path
import argparse

def unorganize_directory(organized_dir: Path, output_dir: Path):
    """
    Walk through every subdirectory and move the files into the parent,
    effectively flattening the directory.
    """
    organized_dir = Path(organized_dir)
    output_dir    = Path(output_dir)
    
    if not organized_dir.exists():
        print(f"Error: Source directory {organized_dir} does not exist")
        return
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    files_moved = 0
    for root, dirs, files in os.walk(organized_dir):
        for file in files:
            source_file      = Path(root) / file
            destination_file = output_dir / file

            counter = 1
            while destination_file.exists():
                stem             = Path(file).stem
                suffix           = Path(file).suffix
                destination_file = output_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            try:
                shutil.move(source_file, destination_file)
                print(f"Moved: {source_file} -> {destination_file}")
                files_moved += 1
            except Exception as e:
                print(f"Error moving {source_file}: {e}")
    
    print(f"\nUnorganize done. Moved {files_moved} files to {output_dir}.")
    cleanup_empty_dirs(organized_dir)

def cleanup_empty_dirs(directory: Path, retries: int):
    """Remove empty directories after unorganizing."""
    retries: int = 3 # maximum retries
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory)
            print(f"Directory: [ {directory} ] has been removed along with its contents.")
        except Exception as e:
            print(f"An error has occurred when removing the directory tree: \n->{e}")
            print(f"Trying again with maximum of 3 retries: {retries=}")
            if retries > 0:
                cleanup_empty_dirs(directory, retries - 1)
    else:
        print(f"OS path does not exist -> [ {directory} ]")

    # ---- The code below removes each subdirectory if it has no contents. ----
    # for root, dirs, files in os.walk(directory, topdown=False):
    #     for dir_name in dirs:
    #         dir_path = Path(root) / dir_name
    #         try:
    #             if not any(dir_path.iterdir()):  # Directory is empty
    #                 dir_path.rmdir()
    #                 print(f"Removed empty directory: {dir_path}")
    #         except OSError:
    #             pass  # Directory not empty or other error

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
