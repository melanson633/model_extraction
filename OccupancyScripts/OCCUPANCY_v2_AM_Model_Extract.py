import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse as date_parse
import logging

# --- CONFIGURATION ---
INPUT_FILES = [
    r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Data\_CF\360 Narragansett AM Model - 022625_Cash Flow_20250319_123019.xls",
    r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Data\_CF\8 Technology Drive AM Model - 041225_Cash Flow_20250413_171605.xlsx",
    r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Data\_CF\153 Rangeway AM Model - 022625_Cash Flow_20250321_085659.xls"
]
OUTPUT_DIR = r"C:\Users\mmelanson\.cursor-tutor\projects\AM Model Extraction\Output\Occupancy"
SHEET_NAME = "Cash Flow"
LOG_FILE = os.path.join(OUTPUT_DIR, "occupancy_extraction_v2.log")

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

    if None in [row_months, row_occupied, row_building, row_avg_occ]:
        for field, row in zip(
            ["For the Months", "Occupied Area", "Building Area", "Average Occupancy Percentage"],
            [row_months, row_occupied, row_building, row_avg_occ]
        ):
            if row is None:
                log_missing(field, filepath)
        logging.info(f"Skipping file due to missing anchors: {filepath}")
        return

    # Extract headers and data rows
    header_row = df.iloc[row_months, 1:].tolist()
    months = parse_month_headers(header_row)
    occupied = parse_numeric_row(df.iloc[row_occupied, 1:].tolist())
    building = parse_numeric_row(df.iloc[row_building, 1:].tolist())
    avg_occ = parse_percentage_row(df.iloc[row_avg_occ, 1:].tolist())

    logging.info(f"Extracted {len(months)} months, {len(occupied)} occupied, {len(building)} building, {len(avg_occ)} avg occupancy values.")

    # Only keep columns where month is valid
    data = []
    for i, month in enumerate(months):
        if month is not None:
            occ = occupied[i] if i < len(occupied) else np.nan
            bldg = building[i] if i < len(building) else np.nan
            avg = avg_occ[i] if i < len(avg_occ) else np.nan
            data.append([property_name, month, occ, bldg, avg])
            logging.debug(f"Row {i}: {property_name}, {month}, {occ}, {bldg}, {avg}")

    if not data:
        logging.warning(f"No valid data extracted from file: {filepath}")
        return

    # Save to CSV
    out_df = pd.DataFrame(data, columns=["PROPERTY", "MONTH", "OCCUPIED SF", "TOTAL BUILDING SF", "AVG. OCCUPANCY %"])
    out_path = os.path.join(OUTPUT_DIR, f"{property_name}_OCCUPANCY.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        out_df.to_csv(out_path, index=False, header=True, date_format='%Y-%m-%d')
        logging.info(f"Saved CSV: {out_path}")
    except Exception as e:
        logging.error(f"Failed to save CSV for {filepath}: {e}")

# --- RUN SCRIPT ---
if __name__ == "__main__":
    logging.info("Starting occupancy extraction script (v2)...")
    for file in INPUT_FILES:
        process_file(file)
    logging.info("Script complete.") 