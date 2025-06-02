import os
import csv
import datetime

# --- Configuration ---
FINANCIALS_CSV_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output\FINANCIALS"
PROPERTY_MAPPING_CSV_PATH = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\FinancialScripts\unique_properties_dictionary_20250529_135353.csv"
OUTPUT_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output"
OUTPUT_FILENAME_BASE = "combined_financials"

# Filters
TARGET_CATEGORIES = {"DEBT", "PRINCIPAL PAYMENT", "INTEREST EXPENSE"} # Case-sensitive
# Dates after April 2025 means from May 1, 2025, onwards
DATE_FILTER_THRESHOLD = datetime.date(2025, 5, 1)

# Column names in your property mapping CSV file
# This is the header for the column with the ORIGINAL property names (as found in FINANCIALS_CSV_DIR files)
PROPERTY_MAP_KEY_COLUMN = "MODEL_UniqueProperty"
# This is the header for the column with the NEW, MAPPED property names
PROPERTY_MAP_VALUE_COLUMN = "DebtTerms_Property" 

# Expected headers in the input financial CSVs. The script will output these columns.
EXPECTED_INPUT_HEADERS = ["CATEGORY", "MONTH", "AMOUNT", "PROPERTY"]

def generate_timestamped_filename(base_name: str, extension=".csv") -> str:
    """Generates a filename with a timestamp (e.g., base_name_YYYYMMDD_HHMMSS.csv)."""
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"

def load_property_mapping(mapping_csv_path: str) -> tuple[dict, list]:
    """Loads the property mapping from the CSV file.
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
                    f"Error: Mapping CSV ({mapping_csv_path}) must contain columns named "
                    f"'{PROPERTY_MAP_KEY_COLUMN}' and '{PROPERTY_MAP_VALUE_COLUMN}'."
                )
                return mapping, errors
            
            for row_num, row in enumerate(reader, 1):
                original_property = row.get(PROPERTY_MAP_KEY_COLUMN)
                mapped_property = row.get(PROPERTY_MAP_VALUE_COLUMN)

                if original_property is None or not str(original_property).strip():
                    errors.append(f"Warning: Row {row_num} in mapping CSV has empty or missing '{PROPERTY_MAP_KEY_COLUMN}'. Skipping.")
                    continue
                
                original_property = str(original_property).strip()
                
                if mapped_property is None or not str(mapped_property).strip():
                    errors.append(f"Warning: Row {row_num} for original property '{original_property}' in mapping CSV "
                                  f"has empty or missing '{PROPERTY_MAP_VALUE_COLUMN}'. It will not be remapped effectively.")
                    # We can choose to map it to itself or skip adding it to the explicit map
                    # For now, if MAPPED_PROPERTY is blank, it won't be in the map, so .get() will return original later.
                else:
                    if original_property in mapping:
                        errors.append(f"Warning: Duplicate original property '{original_property}' found in mapping CSV (row {row_num}). "
                                      f"Using the last encountered mapping: '{str(mapped_property).strip()}'.")
                    mapping[original_property] = str(mapped_property).strip()

    except FileNotFoundError:
        errors.append(f"Error: Property mapping CSV not found at {mapping_csv_path}")
    except Exception as e:
        errors.append(f"An unexpected error occurred while loading property mapping: {e}")
    
    if not mapping and not errors:
        errors.append("Warning: Property mapping file was loaded but is empty or no valid mappings were found.")
        
    return mapping, errors

def main():
    """
    Combines data from all CSVs in FINANCIALS_CSV_DIR,
    remaps PROPERTY column, filters by CATEGORY and MONTH,
    and saves the output to a new timestamped CSV.
    """
    print("Starting financial data combination and filtering process...")

    property_mapping, mapping_errors = load_property_mapping(PROPERTY_MAPPING_CSV_PATH)

    if mapping_errors:
        print("\n--- Property Mapping File Issues ---")
        for error in mapping_errors:
            print(error)
        if f"Error: Property mapping CSV not found at {PROPERTY_MAPPING_CSV_PATH}" in "\n".join(mapping_errors) or \
           f"Error: Mapping CSV ({PROPERTY_MAPPING_CSV_PATH}) must contain columns named" in "\n".join(mapping_errors):
            print("Critical error in mapping file. Please fix and try again. Exiting.")
            return
        print("---")
    
    if not property_mapping:
        print("Warning: Property mapping is empty. Property names will not be remapped.")
    else:
        print(f"Successfully loaded {len(property_mapping)} property mappings.")

    combined_data = []
    unmapped_properties_encountered = set()
    processed_files_count = 0
    rows_processed_total = 0
    rows_passing_filters_total = 0

    if not os.path.isdir(FINANCIALS_CSV_DIR):
        print(f"Error: Input directory for financial CSVs not found: {FINANCIALS_CSV_DIR}")
        return

    for filename in os.listdir(FINANCIALS_CSV_DIR):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(FINANCIALS_CSV_DIR, filename)
            print(f"\nProcessing file: {file_path}...")
            try:
                with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile)
                    
                    # Validate headers for each file
                    missing_headers = [h for h in EXPECTED_INPUT_HEADERS if h not in reader.fieldnames]
                    if missing_headers:
                        print(f"  Warning: File {filename} is missing expected columns: {', '.join(missing_headers)}. Skipping this file.")
                        continue

                    processed_files_count += 1
                    file_rows_processed = 0
                    file_rows_passed = 0

                    for row_num, row in enumerate(reader, 1):
                        file_rows_processed +=1
                        rows_processed_total +=1
                        try:
                            # 1. Date Filter
                            month_str = row["MONTH"]
                            try:
                                month_date = datetime.datetime.strptime(month_str, "%Y-%m-%d").date()
                            except ValueError:
                                print(f"  Warning: Row {row_num} in {filename} has invalid MONTH format '{month_str}'. Skipping row.")
                                continue
                            
                            if month_date < DATE_FILTER_THRESHOLD:
                                continue # Skip row if before threshold

                            # 2. Category Filter
                            category = str(row["CATEGORY"]).strip()
                            if category not in TARGET_CATEGORIES:
                                continue # Skip row if not in target categories

                            # If we reach here, filters passed
                            file_rows_passed += 1
                            rows_passing_filters_total += 1

                            # 3. Remap Property
                            original_property = str(row["PROPERTY"]).strip()
                            mapped_property = property_mapping.get(original_property, original_property)
                            
                            if original_property not in property_mapping and original_property:
                                unmapped_properties_encountered.add(original_property)
                            
                            # 4. Process AMOUNT column for positivity and format
                            amount_str = row["AMOUNT"]
                            formatted_amount = "0.00" # Default in case of error
                            try:
                                amount_val = float(amount_str)
                                positive_amount = abs(amount_val)
                                formatted_amount = f"{positive_amount:.2f}"
                            except ValueError:
                                print(f"  Warning: Row {row_num} in {filename} has non-numeric or empty AMOUNT '{amount_str}'. Using '{formatted_amount}'.")
                            except TypeError: # Handles if amount_str is None
                                print(f"  Warning: Row {row_num} in {filename} has NoneType AMOUNT. Using '{formatted_amount}'.")

                            # Prepare output row
                            output_row = {
                                "CATEGORY": category,
                                "MONTH": month_str, # Keep original string format for month
                                "AMOUNT": formatted_amount, # Use the processed amount
                                "PROPERTY": mapped_property
                            }
                            combined_data.append(output_row)

                        except KeyError as ke:
                            print(f"  Warning: Row {row_num} in {filename} is missing an expected key: {ke}. Skipping row.")
                        except Exception as e_row:
                            print(f"  Error processing row {row_num} in {filename}: {e_row}. Skipping row.")
                    
                    print(f"  Processed {file_rows_processed} rows from {filename}. {file_rows_passed} rows passed filters.")

            except Exception as e_file:
                print(f"  An unexpected error occurred while processing file {filename}: {e_file}")
    
    if processed_files_count == 0:
        print("\nNo CSV files were found or processed in the input directory.")
        return

    print(f"\n--- Summary ---")
    print(f"Total files processed: {processed_files_count}")
    print(f"Total rows read from all files: {rows_processed_total}")
    print(f"Total rows passing all filters: {rows_passing_filters_total}")

    if unmapped_properties_encountered:
        print("\nWarning: The following original property names were encountered but not found in the mapping CSV:")
        for prop_name in sorted(list(unmapped_properties_encountered)):
            print(f"  - {prop_name}")
        print("These properties were included in the output using their original names.")

    if not combined_data:
        print("\nNo data passed all filters. Output file will not be created.")
        return

    output_csv_filename = generate_timestamped_filename(OUTPUT_FILENAME_BASE)
    output_csv_path = os.path.join(OUTPUT_DIR, output_csv_filename)

    try:
        if not os.path.isdir(OUTPUT_DIR):
            print(f"Output directory {OUTPUT_DIR} does not exist. Creating it.")
            os.makedirs(OUTPUT_DIR) # Create directory if it doesn't exist
            
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            # Use the order from EXPECTED_INPUT_HEADERS for the writer
            writer = csv.DictWriter(outfile, fieldnames=EXPECTED_INPUT_HEADERS)
            writer.writeheader()
            writer.writerows(combined_data)
        print(f"\nSuccessfully combined, filtered, and remapped data to: {output_csv_path}")
        print(f"{len(combined_data)} rows written to the output file.")
    except IOError as e:
        print(f"Error writing combined data to CSV file {output_csv_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during output CSV writing: {e}")

if __name__ == "__main__":
    main() 