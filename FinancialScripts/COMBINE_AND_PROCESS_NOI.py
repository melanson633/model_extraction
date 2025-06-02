import os
import csv
import datetime

# --- Configuration ---
OCCUPANCY_CSV_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output\OCCUPANCY"
NOI_PROPERTY_MAPPING_CSV_PATH = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\FinancialScripts\noi_unique_properties_dictionary_20250529_143116.csv"
OUTPUT_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output"
OUTPUT_FILENAME_PREFIX = "noi_"
OUTPUT_FILENAME_BASE = "combined_occupancy_data"

# Column names in your NOI property mapping CSV file
# This is the header for the column with the ORIGINAL property names (as found in OCCUPANCY_CSV_DIR files)
PROPERTY_MAP_KEY_COLUMN = "MODEL_UniqueProperty"
# This is the header for the column with the NEW, MAPPED property names for NOI
PROPERTY_MAP_VALUE_COLUMN = "DebtTerms_Property" 

# Columns to keep in the output file, and their order
OUTPUT_COLUMNS = ["PROPERTY", "MONTH", "F12 NOI"]
# Expected key columns in input CSVs (Property for mapping, Month and F12 NOI for data)
# Ensure these columns actually exist in your source Occupancy CSVs.
REQUIRED_INPUT_COLUMNS_FOR_PROCESSING = ["PROPERTY", "MONTH", "F12 NOI"]

def generate_timestamped_filename(prefix: str, base_name: str, extension=".csv") -> str:
    """Generates a filename with a prefix and timestamp (e.g., prefix_base_name_YYYYMMDD_HHMMSS.csv)."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}{base_name}_{timestamp}{extension}"

def load_noi_property_mapping(mapping_csv_path: str) -> tuple[dict, list]:
    """Loads the NOI property mapping from the CSV file.
    Returns a tuple: (mapping_dictionary, errors_list)
    """
    mapping = {}
    errors = []
    try:
        with open(mapping_csv_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            if PROPERTY_MAP_KEY_COLUMN not in reader.fieldnames or \
               PROPERTY_MAP_VALUE_COLUMN not in reader.fieldnames:
                errors.append(
                    f"Error: NOI Property Mapping CSV ({mapping_csv_path}) must contain columns named "
                    f"'{PROPERTY_MAP_KEY_COLUMN}' and '{PROPERTY_MAP_VALUE_COLUMN}'."
                )
                return mapping, errors
            
            for row_num, row in enumerate(reader, 1):
                original_property = row.get(PROPERTY_MAP_KEY_COLUMN)
                mapped_property = row.get(PROPERTY_MAP_VALUE_COLUMN)

                if original_property is None or not str(original_property).strip():
                    errors.append(f"Warning: Row {row_num} in NOI mapping CSV has empty or missing '{PROPERTY_MAP_KEY_COLUMN}'. Skipping.")
                    continue
                original_property = str(original_property).strip()
                
                if mapped_property is None or not str(mapped_property).strip():
                    errors.append(f"Warning: Row {row_num} for original property '{original_property}' in NOI mapping CSV "
                                  f"has empty or missing '{PROPERTY_MAP_VALUE_COLUMN}'. It will effectively not be remapped.")
                else:
                    if original_property in mapping:
                        errors.append(f"Warning: Duplicate original property '{original_property}' found in NOI mapping CSV (row {row_num}). "
                                      f"Using the last encountered mapping: '{str(mapped_property).strip()}'.")
                    mapping[original_property] = str(mapped_property).strip()

    except FileNotFoundError:
        errors.append(f"Error: NOI Property mapping CSV not found at {mapping_csv_path}")
    except Exception as e:
        errors.append(f"An unexpected error occurred while loading NOI property mapping: {e}")
    
    if not mapping and not errors:
        errors.append("Warning: NOI Property mapping file was loaded but is empty or no valid mappings were found.")
        
    return mapping, errors

def main():
    """
    Combines data from all CSVs in OCCUPANCY_CSV_DIR,
    remaps PROPERTY column using the NOI mapping, keeps specified columns,
    and saves the output to a new timestamped CSV.
    """
    print("Starting NOI data combination and processing...")

    noi_property_mapping, mapping_errors = load_noi_property_mapping(NOI_PROPERTY_MAPPING_CSV_PATH)

    if mapping_errors:
        print("\n--- NOI Property Mapping File Issues ---")
        for error in mapping_errors:
            print(error)
        critical_error_in_mapping = any(
            err_msg.startswith("Error: NOI Property mapping CSV not found") or 
            err_msg.startswith("Error: NOI Property Mapping CSV") 
            for err_msg in mapping_errors
        )
        if critical_error_in_mapping:
            print("Critical error in NOI mapping file. Please fix and try again. Exiting.")
            return
        print("---")
    
    if not noi_property_mapping:
        print("Warning: NOI Property mapping is empty. Property names will not be remapped.")
    else:
        print(f"Successfully loaded {len(noi_property_mapping)} NOI property mappings.")

    combined_data = []
    unmapped_noi_properties_encountered = set()
    processed_files_count = 0
    rows_processed_total = 0
    rows_selected_total = 0

    if not os.path.isdir(OCCUPANCY_CSV_DIR):
        print(f"Error: Input directory for occupancy CSVs not found: {OCCUPANCY_CSV_DIR}")
        return

    for filename in os.listdir(OCCUPANCY_CSV_DIR):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(OCCUPANCY_CSV_DIR, filename)
            print(f"\nProcessing file: {file_path}...")
            try:
                with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Validate that all required columns for processing are present in this input file
                    missing_required_cols = [col for col in REQUIRED_INPUT_COLUMNS_FOR_PROCESSING if col not in reader.fieldnames]
                    if missing_required_cols:
                        print(f"  Warning: File {filename} is missing required columns: {', '.join(missing_required_cols)}. Skipping this file.")
                        continue

                    processed_files_count += 1
                    file_rows_processed = 0
                    file_rows_selected = 0

                    for row_num, row in enumerate(reader, 1):
                        file_rows_processed += 1
                        rows_processed_total += 1
                        try:
                            # 1. Remap Property
                            original_property = str(row["PROPERTY"]).strip()
                            mapped_property = noi_property_mapping.get(original_property, original_property)
                            
                            if original_property not in noi_property_mapping and original_property:
                                unmapped_noi_properties_encountered.add(original_property)
                            
                            # 2. Select and prepare output row with only specified columns
                            output_row = {}
                            all_output_cols_present = True
                            for col_name in OUTPUT_COLUMNS:
                                if col_name == "PROPERTY":
                                    output_row[col_name] = mapped_property
                                elif col_name in row:
                                    output_row[col_name] = row[col_name]
                                else:
                                    # This should ideally be caught by REQUIRED_INPUT_COLUMNS_FOR_PROCESSING if also in OUTPUT_COLUMNS
                                    # but if F12 NOI (or other output cols not in required) is missing, handle it.
                                    print(f"  Warning: Row {row_num} in {filename} is missing column '{col_name}' needed for output. Skipping row.")
                                    all_output_cols_present = False
                                    break 
                            
                            if all_output_cols_present:
                                combined_data.append(output_row)
                                file_rows_selected += 1
                                rows_selected_total += 1

                        except KeyError as ke:
                            # This error might occur if a column in REQUIRED_INPUT_COLUMNS_FOR_PROCESSING was
                            # somehow not caught by the initial fieldname check for the file.
                            print(f"  Warning: Row {row_num} in {filename} is missing an expected key for processing: {ke}. Skipping row.")
                        except Exception as e_row:
                            print(f"  Error processing row {row_num} in {filename}: {e_row}. Skipping row.")
                    
                    print(f"  Processed {file_rows_processed} rows from {filename}. {file_rows_selected} rows selected for output.")

            except Exception as e_file:
                print(f"  An unexpected error occurred while processing file {filename}: {e_file}")
    
    if processed_files_count == 0:
        print("\nNo CSV files were found or processed in the input directory.")
        return

    print(f"\n--- Summary ---")
    print(f"Total files processed: {processed_files_count}")
    print(f"Total rows read from all files: {rows_processed_total}")
    print(f"Total rows selected for output: {rows_selected_total}")

    if unmapped_noi_properties_encountered:
        print("\nWarning: The following original property names from Occupancy CSVs were encountered but not found in the NOI mapping CSV:")
        for prop_name in sorted(list(unmapped_noi_properties_encountered)):
            print(f"  - {prop_name}")
        print("These properties were included in the output using their original names.")

    if not combined_data:
        print("\nNo data was selected for output. Output file will not be created.")
        return

    output_csv_filename = generate_timestamped_filename(OUTPUT_FILENAME_PREFIX, OUTPUT_FILENAME_BASE)
    output_csv_path = os.path.join(OUTPUT_DIR, output_csv_filename)

    try:
        if not os.path.isdir(OUTPUT_DIR):
            print(f"Output directory {OUTPUT_DIR} does not exist. Creating it.")
            os.makedirs(OUTPUT_DIR)
            
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=OUTPUT_COLUMNS)
            writer.writeheader()
            writer.writerows(combined_data)
        print(f"\nSuccessfully combined and processed NOI data to: {output_csv_path}")
        print(f"{len(combined_data)} rows written to the output file.")
    except IOError as e:
        print(f"Error writing combined NOI data to CSV file {output_csv_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during output CSV writing: {e}")

if __name__ == "__main__":
    main() 