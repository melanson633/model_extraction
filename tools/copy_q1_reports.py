import argparse
import os
import shutil
from pathlib import Path

def copy_q1_reports(src_dir: str, dst_dir: str, verbose: bool = False) -> None:
    """
    Copies Excel files containing "Q1 2025 Report" (case-insensitive) from a source
    directory and its subdirectories to a destination directory.

    Args:
        src_dir: The source directory to search for files.
        dst_dir: The destination directory to copy files to.
        verbose: If True, prints a detailed summary of operations.
    """
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)

    if not src_path.is_dir():
        print(f"Error: Source directory '{src_dir}' does not exist or is not a directory.")
        return

    # Ensure the destination directory exists
    dst_path.mkdir(parents=True, exist_ok=True)

    files_scanned = 0
    files_copied_count = 0
    files_overwritten_count = 0
    copied_files_paths = []
    overwritten_files_paths = []

    for root, _, files in os.walk(src_path):
        for file in files:
            files_scanned += 1
            # Match files with pattern *Q1 2025 Report*.xls[xm]? (case-insensitive)
            if "q1 2025 report" in file.lower() and \
               (file.lower().endswith(".xlsx") or \
                file.lower().endswith(".xlsm") or \
                file.lower().endswith(".xls")):
                
                source_file_path = Path(root) / file
                destination_file_path = dst_path / file

                if verbose:
                    print(f"Found matching file: {source_file_path}")

                try:
                    if destination_file_path.exists():
                        if verbose:
                            print(f"Overwriting existing file: {destination_file_path}")
                        overwritten_files_paths.append(str(destination_file_path))
                        files_overwritten_count += 1
                    
                    shutil.copy2(source_file_path, destination_file_path)
                    copied_files_paths.append(str(destination_file_path))
                    files_copied_count += 1
                    if verbose and destination_file_path not in overwritten_files_paths: # Only print if not already printed as overwritten
                        print(f"Copied: {source_file_path} -> {destination_file_path}")

                except Exception as e:
                    print(f"Error copying file {source_file_path}: {e}")

    if verbose:
        print("\\n--- Summary ---")
        print(f"Total files scanned: {files_scanned}")
        print(f"Total files copied: {files_copied_count}")
        if files_copied_count > 0:
            print("Copied files:")
            for p in copied_files_paths:
                print(f"  - {p}")
        print(f"Total files overwritten: {files_overwritten_count}")
        if files_overwritten_count > 0:
            print("Overwritten files:")
            for p in overwritten_files_paths:
                print(f"  - {p}")
        if files_copied_count == 0 and files_overwritten_count == 0:
            print("No matching files found to copy.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Copy Q1 2025 report files from a source to a destination directory.',
        formatter_class=argparse.RawTextHelpFormatter # To allow newlines in help text
    )
    parser.add_argument(
        '--src',
        type=str,
        required=True,
        help='Source directory to search for Excel files.\\nExample: "P:\\\\Buildings & Land(s)\\\\Portfolio Sales\\\\2025 - New JLL Portfolio Wide\\\\AM Model Cash Flows"'
    )
    parser.add_argument(
        '--dst',
        type=str,
        required=True,
        help='Destination directory to copy files to.\\nExample: "C:\\\\Users\\\\mmelanson\\\\.cursor-tutor\\\\projects\\\\AM Model Extraction\\\\Data\\\\_MODEL"'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output to show detailed progress and summary.'
    )

    args = parser.parse_args()

    copy_q1_reports(args.src, args.dst, args.verbose) 