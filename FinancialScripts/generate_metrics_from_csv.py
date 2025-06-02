import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

# --- CONFIGURATION ---
# Fix paths to use the project root directory instead of relative to the script
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_DIR = os.path.join(PROJECT_ROOT, 'Output', 'FINANCIALS')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'Output', 'METRICS')
OUTPUT_PREFIX = 'metrics_'

# Print paths for debugging
print(f"Project Root: {PROJECT_ROOT}")
print(f"Input Directory: {INPUT_DIR}")
print(f"Output Directory: {OUTPUT_DIR}")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)  # Create input dir if it doesn't exist

# Categories for BASIS calculation
BASIS_CATEGORIES = [
    'CAPEX',
    'ACQ, DISPO, REFI COSTS',
    'LEASING COMMISSIONS',
    'TENANT IMPROVEMENTS'
]
DEBT_CATEGORY = 'DEBT'
NOI_CATEGORY = 'NOI'

# --- UTILITY FUNCTIONS ---
def parse_month(date_str):
    """
    Parse a date string in YYYY-MM-DD format and return a datetime.date object (first of month).
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None

def log_warning(msg):
    warnings.warn(msg)

# --- MAIN PROCESSING ---
def process_file(input_path):
    # Read input CSV
    try:
        df = pd.read_csv(input_path, dtype={'CATEGORY': str, 'MONTH': str, 'AMOUNT': float, 'PROPERTY': str})
    except Exception as e:
        print(f"[ERROR] Could not read {input_path}: {e}")
        return None

    # Parse MONTH as datetime.date
    df['MONTH'] = df['MONTH'].apply(parse_month)
    df = df.dropna(subset=['MONTH'])
    df = df.sort_values('MONTH')

    # Get unique PROPERTY (should be only one per file)
    property_vals = df['PROPERTY'].unique()
    if len(property_vals) != 1:
        log_warning(f"File {os.path.basename(input_path)}: Expected one PROPERTY value, found {property_vals}. Using first.")
    property_val = property_vals[0]

    # Get all unique months in ascending order
    all_months = sorted(df['MONTH'].unique())

    # Precompute NOI by month for rolling window
    noi_df = df[df['CATEGORY'] == NOI_CATEGORY][['MONTH', 'AMOUNT']].copy()
    noi_df = noi_df.groupby('MONTH', as_index=False)['AMOUNT'].sum()
    noi_months = set(noi_df['MONTH'])

    # Precompute BASIS and DEBT cumulative sums by month
    basis_df = df[df['CATEGORY'].isin(BASIS_CATEGORIES)][['MONTH', 'AMOUNT']].copy()
    basis_df = basis_df.groupby('MONTH', as_index=False)['AMOUNT'].sum()
    debt_df = df[df['CATEGORY'] == DEBT_CATEGORY][['MONTH', 'AMOUNT']].copy()
    debt_df = debt_df.groupby('MONTH', as_index=False)['AMOUNT'].sum()

    # Build cumulative sums for BASIS and DEBT
    basis_cumsum = basis_df.set_index('MONTH').reindex(all_months, fill_value=0.0)['AMOUNT'].cumsum()
    debt_cumsum = debt_df.set_index('MONTH').reindex(all_months, fill_value=0.0)['AMOUNT'].cumsum()

    # Prepare output rows
    output_rows = []
    for idx, month in enumerate(all_months):
        # F12 NOI: sum of NOI for next 12 months (excluding current month)
        start = month + timedelta(days=1)  # next day after current month
        end = (month.replace(day=1) + pd.DateOffset(months=12)).date()
        # Get months strictly after current month, up to 12 months ahead
        noi_window = noi_df[(noi_df['MONTH'] > month) & (noi_df['MONTH'] <= end)]
        f12_noi = noi_window['AMOUNT'].sum() if not noi_window.empty else 0.0

        # BASIS cumulative sum up to and including current month (flip sign to positive)
        basis_val = -basis_cumsum.loc[month] if month in basis_cumsum else 0.0
        # DEBT BALANCE cumulative sum up to and including current month
        debt_val = debt_cumsum.loc[month] if month in debt_cumsum else 0.0

        output_rows.append({
            'PROPERTY': property_val,
            'MONTH': month.strftime('%Y-%m-%d'),
            'F12 NOI': round(f12_noi, 2),
            'BASIS': round(basis_val, 2),
            'DEBT BALANCE': round(debt_val, 2)
        })

    # Check for missing categories
    for cat in [NOI_CATEGORY] + BASIS_CATEGORIES + [DEBT_CATEGORY]:
        if cat not in df['CATEGORY'].values:
            log_warning(f"File {os.path.basename(input_path)}: Missing category '{cat}' in data.")

    # Output DataFrame
    out_df = pd.DataFrame(output_rows, columns=['PROPERTY', 'MONTH', 'F12 NOI', 'BASIS', 'DEBT BALANCE'])
    return out_df, property_val, all_months


def main():
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory does not exist: {INPUT_DIR}")
        print("Creating directory now, but it contains no CSV files to process.")
        os.makedirs(INPUT_DIR, exist_ok=True)
        return
        
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.csv') and not f.startswith(OUTPUT_PREFIX)]
    if not files:
        print(f"No input CSV files found in {INPUT_DIR}.")
        return
    for fname in files:
        input_path = os.path.join(INPUT_DIR, fname)
        output_name = OUTPUT_PREFIX + os.path.splitext(fname)[0] + '.csv'
        output_path = os.path.join(OUTPUT_DIR, output_name)
        result = process_file(input_path)
        if result is None:
            continue
        out_df, property_val, all_months = result
        out_df.to_csv(output_path, index=False, float_format='%.2f')
        # Print summary
        first_month = out_df['MONTH'].iloc[0] if not out_df.empty else 'N/A'
        last_month = out_df['MONTH'].iloc[-1] if not out_df.empty else 'N/A'
        print(f"Processed: {fname} | Rows: {len(out_df)} | First MONTH: {first_month} | Last MONTH: {last_month}")
        print(f"Output saved to: {output_path}")

if __name__ == '__main__':
    main() 