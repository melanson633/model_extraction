import os
import csv
import datetime

# Directory containing the CSV files from which to extract property names
OCCUPANCY_CSV_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output\OCCUPANCY"
# Output directory for the new properties dictionary
OUTPUT_SCRIPT_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\FinancialScripts"

# --- Configuration for the output file ---
OUTPUT_FILENAME_PREFIX = "noi_"
OUTPUT_FILENAME_BASE = "unique_properties_dictionary"
# The column header for the properties in the output file (for manual mapping)
OUTPUT_HEADER = "MODEL_UniqueProperty" # Consistent with other property sampling scripts
# The column name to read property names from in the input CSVs
INPUT_PROPERTY_COLUMN_NAME = "PROPERTY" # Assuming this is the column name in occupancy CSVs

def generate_timestamped_filename(prefix: str, base_name: str) -> str:
    """Generates a filename with a prefix and timestamp (e.g., prefix_base_name_YYYYMMDD_HHMMSS.csv)."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}{base_name}_{timestamp}.csv"

def main():
    """
    Scans CSV files in OCCUPANCY_CSV_DIR, extracts unique values from the
    INPUT_PROPERTY_COLUMN_NAME column, and writes them to a new timestamped CSV file
    in the OUTPUT_SCRIPT_DIR directory with the 'noi_' prefix.
    """
    if not os.path.isdir(OUTPUT_SCRIPT_DIR):
        print(f"Output directory {OUTPUT_SCRIPT_DIR} does not exist. Creating it.")
        try:
            os.makedirs(OUTPUT_SCRIPT_DIR)
        except OSError as e:
            print(f"Error: Could not create output directory {OUTPUT_SCRIPT_DIR}: {e}")
            return
            
    output_csv_filename = generate_timestamped_filename(OUTPUT_FILENAME_PREFIX, OUTPUT_FILENAME_BASE)
    output_csv_path = os.path.join(OUTPUT_SCRIPT_DIR, output_csv_filename)

    all_found_properties = set()

    print(f"Starting property name extraction from CSVs in: {OCCUPANCY_CSV_DIR}")

    if not os.path.isdir(OCCUPANCY_CSV_DIR):
        print(f"Error: Source directory not found - {OCCUPANCY_CSV_DIR}")
        print("Please ensure the path is correct.")
        return

    processed_files_count = 0
    for filename in os.listdir(OCCUPANCY_CSV_DIR):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(OCCUPANCY_CSV_DIR, filename)
            print(f"Processing file: {file_path}...")
            try:
                with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile: # utf-8-sig handles BOM
                    reader = csv.DictReader(csvfile)
                    
                    if INPUT_PROPERTY_COLUMN_NAME not in reader.fieldnames:
                        print(f"  Warning: Column '{INPUT_PROPERTY_COLUMN_NAME}' not found in {filename}. Skipping this file.")
                        continue
                    
                    file_properties_count = 0
                    for row_number, row in enumerate(reader, 1):
                        try:
                            property_name = row.get(INPUT_PROPERTY_COLUMN_NAME) # Use .get() for safer access
                            if property_name is not None and str(property_name).strip(): # Ensure property name is not None or empty
                                all_found_properties.add(str(property_name).strip())
                                file_properties_count += 1
                        except KeyError: # Should be caught by fieldnames check, but as a safeguard
                            print(f"  Error: Column '{INPUT_PROPERTY_COLUMN_NAME}' missing in a row in {filename} (should not happen if header check passed).")
                            break 
                            
                    if file_properties_count > 0:
                        print(f"  Extracted {file_properties_count} property name instances (unique ones added to set) from this file.")
                    else:
                        print(f"  No property names found or extracted from {filename} (column '{INPUT_PROPERTY_COLUMN_NAME}' might be missing or empty).")
                    processed_files_count += 1

            except FileNotFoundError:
                print(f"  Error: File not found during processing - {file_path}. Skipping.")
            except Exception as e:
                print(f"  An unexpected error occurred while processing file {filename}: {e}")
                print(f"  Skipping this file due to the error.")
    
    if processed_files_count == 0:
        print("\nNo CSV files were found or processed in the specified directory.")
        return

    if not all_found_properties:
        print("\nNo unique property names were found in any of the processed CSV files.")
        return

    sorted_properties = sorted(list(all_found_properties))

    print(f"\nFound a total of {len(sorted_properties)} unique property names across all processed files.")

    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow([OUTPUT_HEADER]) 
            for prop_name in sorted_properties:
                writer.writerow([prop_name])
        print(f"Successfully wrote {len(sorted_properties)} unique property names to: {output_csv_path}")
        print(f"You can now open this file, add your mapping column, and use it to create your property mapping dictionary for NOI data.")
    except IOError as e:
        print(f"Error writing unique property names to CSV file {output_csv_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == "__main__":
    main() 