import os
import csv
import datetime

# Directory containing the CSV files from which to extract categories
FINANCIALS_CSV_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output\FINANCIALS"

# --- Configuration for the output file ---
OUTPUT_FILENAME_BASE = "rebuilt_unique_categories"
# The column header for the categories in the output file (useful for rebuilding the mapping)
OUTPUT_HEADER = "MODEL_UniqueCategory" 
# The column name to read categories from in the input CSVs
INPUT_CATEGORY_COLUMN_NAME = "CATEGORY"

def generate_timestamped_filename(base_name: str) -> str:
    """Generates a filename with a timestamp (e.g., base_name_YYYYMMDD_HHMMSS.csv)."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.csv"

def main():
    """
    Scans CSV files in FINANCIALS_CSV_DIR, extracts unique values from the
    INPUT_CATEGORY_COLUMN_NAME column, and writes them to a new timestamped CSV file
    in the same directory as this script.
    """
    script_dir = os.path.dirname(__file__)
    output_csv_filename = generate_timestamped_filename(OUTPUT_FILENAME_BASE)
    output_csv_path = os.path.join(script_dir, output_csv_filename)

    all_found_categories = set()

    print(f"Starting category extraction from CSVs in: {FINANCIALS_CSV_DIR}")

    if not os.path.isdir(FINANCIALS_CSV_DIR):
        print(f"Error: Source directory not found - {FINANCIALS_CSV_DIR}")
        print("Please ensure the path is correct.")
        return

    processed_files_count = 0
    for filename in os.listdir(FINANCIALS_CSV_DIR):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(FINANCIALS_CSV_DIR, filename)
            print(f"Processing file: {file_path}...")
            try:
                with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile: # utf-8-sig handles potential BOM
                    reader = csv.DictReader(csvfile)
                    
                    if INPUT_CATEGORY_COLUMN_NAME not in reader.fieldnames:
                        print(f"  Warning: Column '{INPUT_CATEGORY_COLUMN_NAME}' not found in {filename}. Skipping this file's categories.")
                        continue
                    
                    file_categories_count = 0
                    for row_number, row in enumerate(reader, 1):
                        try:
                            category = row[INPUT_CATEGORY_COLUMN_NAME]
                            if category is not None and str(category).strip(): # Ensure category is not None or empty after stripping
                                all_found_categories.add(str(category).strip())
                                file_categories_count += 1
                            # else:
                                # print(f"  Info: Row {row_number} in {filename} has an empty or None category. Skipping.")
                        except KeyError:
                            # This should be caught by the fieldnames check, but as a safeguard:
                            print(f"  Error: Column '{INPUT_CATEGORY_COLUMN_NAME}' missing in a row in {filename} (should not happen if header check passed).")
                            break # Stop processing this file if DictReader fails mid-file
                            
                    if file_categories_count > 0:
                        print(f"  Extracted {file_categories_count} categories from this file.")
                    else:
                        print(f"  No categories found or extracted from {filename} (column might be empty or all values invalid).")
                    processed_files_count += 1

            except FileNotFoundError:
                # This case should ideally not be hit if os.listdir is used, but good practice.
                print(f"  Error: File not found during processing - {file_path}. Skipping.")
            except Exception as e:
                print(f"  An unexpected error occurred while processing file {filename}: {e}")
                print(f"  Skipping this file due to the error.")
    
    if processed_files_count == 0:
        print("\nNo CSV files were found or processed in the specified directory.")
        return

    if not all_found_categories:
        print("\nNo unique categories were found in any of the processed CSV files.")
        return

    sorted_categories = sorted(list(all_found_categories))

    print(f"\nFound a total of {len(sorted_categories)} unique categories across all processed files.")

    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow([OUTPUT_HEADER]) # Write the header for the new mapping file
            for category in sorted_categories:
                writer.writerow([category])
        print(f"Successfully wrote {len(sorted_categories)} unique categories to: {output_csv_path}")
        print(f"You can now open this file, add an 'EXTRACTION_MAPPING' column, and use it to rebuild your main category mapping dictionary.")
    except IOError as e:
        print(f"Error writing unique categories to CSV file {output_csv_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == "__main__":
    main() 