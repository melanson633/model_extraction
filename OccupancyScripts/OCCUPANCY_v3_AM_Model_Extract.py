import os
import re
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse as date_parse
import logging

# --- CONFIGURATION ---
INPUT_FOLDER = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Data\_ARGUS CF"
OUTPUT_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output\Occupancy"
SHEET_NAME = "Cash Flow"
LOG_FILE = os.path.join(OUTPUT_DIR, "occupancy_extraction_v3.log")

# --- SETUP LOGGING ---
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# --- UTILITY FUNCTIONS ---
def extract_property_name(filepath):
    """Extracts the property name from the file name before the first '_' or '-'."""
    base = os.path.basename(filepath)
    match = re.match(r"([^-_]+(?: [^-_]+)*)", base)
    return match.group(1).strip() if match else base.split('.')[0]

def find_anchor_row(df, anchor):
    """Finds the row index of the anchor string in column A."""
    for idx, val in enumerate(df.iloc[:, 0]):
        if isinstance(val, str) and val.strip() == anchor.strip():
            logging.info(f"Found anchor '{anchor}' at row {idx+1}")
            return idx
    logging.warning(f"Anchor '{anchor}' not found.")
    return None

def parse_month_headers(header_row):
    """Converts Excel month headers (e.g., 'Feb-2021') to datetime.date objects."""
    months = []
    for val in header_row:
        if isinstance(val, str):
            try:
                dt = date_parse(val, dayfirst=False, fuzzy=True)
                months.append(dt.replace(day=1).date())
            except Exception:
                months.append(None)
        else:
            months.append(None)
    return months

def parse_numeric_row(row):
    """Converts a row of values to floats or ints, handling NaNs and commas."""
    out = []
    for val in row:
        if pd.isnull(val):
            out.append(np.nan)
        elif isinstance(val, str):
            val = val.replace(',', '').replace('%', '')
            try:
                out.append(float(val))
            except Exception:
                out.append(np.nan)
        else:
            out.append(val)
    return out

def parse_percentage_row(row):
    """Converts a row of percentage strings to floats (e.g., '100.00%' -> 1.0)."""
    out = []
    for val in row:
        if pd.isnull(val):
            out.append(np.nan)
        elif isinstance(val, str) and '%' in val:
            try:
                out.append(float(val.replace('%', '').replace(',', '')) / 100)
            except Exception:
                out.append(np.nan)
        else:
            try:
                out.append(float(val))
            except Exception:
                out.append(np.nan)
    return out

def log_missing(field, file):
    msg = f"Missing '{field}' in file: {file}"
    logging.warning(msg)
    print(f"[WARNING] {msg}")

# --- MAIN PROCESSING FUNCTION ---
def process_file(filepath):
    property_name = extract_property_name(filepath)
    logging.info(f"\n--- Processing file: {filepath} ---")
    ext = os.path.splitext(filepath)[1].lower()
    df = None

    try:
        if ext == ".xlsx":
            try:
                df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=None, engine='openpyxl')
                logging.info(f"Loaded .xlsx file with openpyxl: {filepath}")
            except Exception as e:
                logging.error(f"Failed to open .xlsx file with openpyxl: {e}")
                return
        elif ext == ".xls":
            try:
                import xlrd  # Try to import xlrd
                if int(xlrd.__version__.split('.')[0]) > 1:
                    raise ImportError("xlrd >= 2.0.0 does not support .xls files. Please install xlrd==1.2.0")
                df = pd.read_excel(filepath, sheet_name=SHEET_NAME, header=None, engine='xlrd')
                logging.info(f"Loaded .xls file with xlrd: {filepath}")
            except ImportError as e:
                logging.error(f"xlrd is not installed or wrong version for .xls support: {e}")
                logging.error("To fix: pip install xlrd==1.2.0")
                return
            except Exception as e:
                logging.error(f"Failed to open .xls file with xlrd: {e}")
                return
        else:
            logging.error(f"Unsupported file extension: {ext}")
            return
    except Exception as e:
        logging.error(f"Could not open file: {filepath} ({e})")
        return

    # Find anchor rows
    row_months = find_anchor_row(df, "For the Months")
    row_occupied = find_anchor_row(df, "  Occupied Area")
    row_building = find_anchor_row(df, "  Building Area")
    row_avg_occ = find_anchor_row(df, "  Average Occupancy Percentage")
    
    # Additional anchors for v3
    row_noi = find_anchor_row(df, "Net Operating Income")
    row_tenant_imp = find_anchor_row(df, "  Tenant Improvements")
    row_leasing_comm = find_anchor_row(df, "  Leasing Commissions")

    # Check essential rows are found (without these, we cannot proceed)
    essential_anchors = [row_months, row_occupied, row_building, row_avg_occ, row_noi]
    essential_names = ["For the Months", "Occupied Area", "Building Area", "Average Occupancy Percentage", "Net Operating Income"]
    
    if None in essential_anchors:
        # Log which essential anchors are missing
        for field, row in zip(essential_names, essential_anchors):
            if row is None:
                log_missing(field, filepath)
        logging.info(f"Skipping file due to missing essential anchors: {filepath}")
        return
    
    # Log if optional anchors are missing but continue processing
    optional_anchors = [(row_tenant_imp, "Tenant Improvements"), (row_leasing_comm, "Leasing Commissions")]
    for row, name in optional_anchors:
        if row is None:
            log_missing(name, filepath)
            logging.info(f"Will use default value 0 for '{name}' in file: {filepath}")

    # Extract headers and data rows
    header_row = df.iloc[row_months, 1:].tolist()
    months = parse_month_headers(header_row)
    occupied = parse_numeric_row(df.iloc[row_occupied, 1:].tolist())
    building = parse_numeric_row(df.iloc[row_building, 1:].tolist())
    avg_occ = parse_percentage_row(df.iloc[row_avg_occ, 1:].tolist())
    
    # Extract new fields for v3
    noi = parse_numeric_row(df.iloc[row_noi, 1:].tolist())
    
    # For optional fields, use zeros if anchor not found
    tenant_imp = parse_numeric_row(df.iloc[row_tenant_imp, 1:].tolist()) if row_tenant_imp is not None else [0] * len(header_row)
    leasing_comm = parse_numeric_row(df.iloc[row_leasing_comm, 1:].tolist()) if row_leasing_comm is not None else [0] * len(header_row)

    logging.info(f"Extracted {len(months)} months, {len(occupied)} occupied, {len(building)} building, {len(avg_occ)} avg occupancy values.")
    logging.info(f"Additionally extracted {len(noi)} NOI, {len(tenant_imp)} tenant improvements, {len(leasing_comm)} leasing commissions values.")

    # Only keep columns where month is valid
    data = []
    cutoff_date = datetime(2024, 12, 31).date()  # Cutoff date is 12/31/2024
    
    for i, month in enumerate(months):
        if month is not None:
            # Skip months before the cutoff date
            if month <= cutoff_date:
                logging.debug(f"Skipping month {month} as it's before or equal to cutoff date {cutoff_date}")
                continue
                
            occ = occupied[i] if i < len(occupied) else np.nan
            bldg = building[i] if i < len(building) else np.nan
            avg = avg_occ[i] if i < len(avg_occ) else np.nan
            
            # New fields for v3 - Tenant Improvements and Leasing Commissions remain as is
            tenant_imp_val = round(tenant_imp[i]) if i < len(tenant_imp) and not pd.isnull(tenant_imp[i]) else np.nan
            leasing_comm_val = round(leasing_comm[i]) if i < len(leasing_comm) and not pd.isnull(leasing_comm[i]) else np.nan

            # Calculate 12-month forward-looking NOI
            noi_forward_sum = np.nan  # Default to NaN

            future_start_idx = i + 1
            # The end index for the slice should be i + 12 because slice is exclusive at the end for 12 items
            # e.g. i+1 to i+12 (inclusive) means slice noi[i+1 : i+13]
            future_end_slice_idx = i + 13 

            if future_end_slice_idx <= len(noi): # Check if we have enough data for 12 future months
                next_12_noi_values = noi[future_start_idx : future_end_slice_idx]
                
                # Check if all 12 values are present (not sliced short) and none are NaN
                if len(next_12_noi_values) == 12 and not any(pd.isnull(val) for val in next_12_noi_values):
                    noi_forward_sum = sum(next_12_noi_values)
            
            noi_val = round(noi_forward_sum) if not pd.isnull(noi_forward_sum) else np.nan
            
            data.append([property_name, month, occ, bldg, avg, noi_val, tenant_imp_val, leasing_comm_val])
            logging.debug(f"Row {i}: {property_name}, {month}, {occ}, {bldg}, {avg}, Forward NOI Sum: {noi_val}, TI: {tenant_imp_val}, LC: {leasing_comm_val}")

    if not data:
        logging.warning(f"No valid data extracted from file: {filepath}")
        return

    # Save to CSV with additional columns for v3
    out_df = pd.DataFrame(data, columns=[
        "PROPERTY", "MONTH", "OCCUPIED SF", "TOTAL BUILDING SF", "AVG. OCCUPANCY %",
        "F12 NOI", "TENANT IMPROVEMENTS", "LEASING COMMISSIONS"
    ])
    out_path = os.path.join(OUTPUT_DIR, f"{property_name}_OCCUPANCY.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        out_df.to_csv(out_path, index=False, header=True, date_format='%Y-%m-%d')
        logging.info(f"Saved CSV: {out_path}")
    except Exception as e:
        logging.error(f"Failed to save CSV for {filepath}: {e}")

# --- RUN SCRIPT ---
if __name__ == "__main__":
    logging.info("Starting occupancy extraction script (v3)...")
    
    # Get all Excel files from the input folder
    input_files = []
    for ext in ['.xls', '.xlsx']:
        input_files.extend(glob.glob(os.path.join(INPUT_FOLDER, f'*{ext}')))
    
    logging.info(f"Found {len(input_files)} Excel files to process in folder: {INPUT_FOLDER}")
    
    for file in input_files:
        process_file(file)
        
    logging.info("Script complete.") 